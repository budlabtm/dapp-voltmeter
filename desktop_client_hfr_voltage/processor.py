from PyQt6 import QtCore
from scipy import fft
from .settings import Settings
from collections import deque
from .stream import Source
import numpy
import time


class RingBuffer:
    def __init__(self, maxsize: int, iterable: list):
        self._data = list(iterable)
        self._maxsize = maxsize
        self._size = 0
        self._sum = 0
        self._last = 0

    def append(self, value):
        self._sum += value

        if self._size < self._maxsize:
            self._data.append(value)
            self._size += 1
        else:
            self._sum -= self._data[self._last]
            self._data[self._last] = value
            self._last = self._last + 1 if self._last < self._maxsize - 1 else 0

    def data(self):
        return self._data

    def size(self):
        return self._size

    def mean(self):
        if self._size == 0:
            return 0

        return self._sum / self._size


class StreamBuffer:
    def __init__(self, size: int):
        self._data = deque([0] * size, size)
        self._delays = RingBuffer(size, [])
        self._last_income_time = time.time()

    def append(self, value):
        self._data.pop()
        self._data.appendleft(value)

        income_time = time.time()
        self._delays.append(income_time - self._last_income_time)
        self._last_income_time = income_time

    def data(self):
        return self._data

    def sampling_rate(self):
        if self._delays.mean() == 0:
            return 0

        return 1 / self._delays.mean()

    def delay(self):
        return self._delays.mean()


class Processor(QtCore.QObject):
    updateInstant = QtCore.pyqtSignal(float)
    updateMean = QtCore.pyqtSignal(float)
    updateDeviation = QtCore.pyqtSignal(float)
    updateDirectChartData = QtCore.pyqtSignal(object, object)
    updateFFTChartData = QtCore.pyqtSignal(object, object)
    updateProcessingInterval = QtCore.pyqtSignal(int)
    updateDirectLabel = QtCore.pyqtSignal(str)
    updateFFTLabel = QtCore.pyqtSignal(str)

    def __init__(self, channel: str) -> None:
        super().__init__()
        self.storage = StreamBuffer(
            Settings.get_range('processing_size_range').stop)

        self.processing_rate = int(
            Settings.get_for_channel(channel, 'processing_rate'))
        self.direct_processing_size = int(
            Settings.get_for_channel(channel, 'direct_processing_size'))
        self.fft_processing_size = int(
            Settings.get_for_channel(channel, 'fft_processing_size'))
        self.channel = channel
        self.current_tab = 0
        self.fft_x_converted = Settings.get_for_channel(
            channel, 'fft_x_converted') == 'true'
        self.direct_x_converted = Settings.get_for_channel(
            channel, 'direct_x_converted') == 'true'

        self.instant_timer = QtCore.QTimer()
        self.processing_timer = QtCore.QTimer()

        self.instant_timer.timeout.connect(self.update_instant)
        self.processing_timer.timeout.connect(self.process)
        self.updateProcessingInterval.connect(
            self.processing_timer.setInterval)

        self.instant_timer.start(
            int(1000 / int(Settings.get_for_channel(channel, 'instant_rate'))))
        self.processing_timer.start(int(1000 / self.processing_rate))

    def on_value(self, value):
        self.storage.append(value)

    def update_instant(self):
        self.updateInstant.emit(self.storage.data()[0])

    def process(self):
        if self.current_tab == 0:  # U
            r = self.direct_processing_size
            x2 = numpy.array(range(1, r + 1))
            x1 = x2 * self.storage.delay()
            y = numpy.array(self.storage.data())[:r]

            self.updateMean.emit(y.mean())
            self.updateDeviation.emit(y.std())
            self.updateDirectLabel.emit(
                'Timeline, seconds ago' if self.direct_x_converted else 'Timeline, ticks ago')
            self.updateDirectChartData.emit(
                x1 if self.direct_x_converted else x2, y)

        elif self.current_tab == 1:  # FFT
            r = self.fft_processing_size - 1
            x1 = numpy.array(range(-(r // 2), r // 2 + 1)) / (r - 1)
            x2 = x1 * self.storage.sampling_rate()

            array = numpy.array(self.storage.data())[:r]
            y = numpy.abs(fft.fft(array - array.mean(), norm='forward'))
            y = numpy.concatenate((y[(r // 2):], y[1:(r // 2 + 1)]))

            self.updateFFTLabel.emit(
                'Frequency, Hz' if self.fft_x_converted else 'Frequency')
            self.updateFFTChartData.emit(x2 if self.fft_x_converted else x1, y)

    def set_processing_rate(self, rate: int):
        self.processing_rate = rate
        self.updateProcessingInterval.emit(int(1000 / self.processing_rate))

    def set_current_tab(self, tab: int):
        self.current_tab = tab

    def set_direct_x_converted(self, converted: bool):
        self.direct_x_converted = converted

    def set_fft_x_converted(self, converted: bool):
        self.fft_x_converted = converted

    def set_direct_processing_size(self, size: int):
        self.direct_processing_size = size

    def set_fft_processing_size(self, size: int):
        self.fft_processing_size = size

    def attach_source(self, source: Source):
        source.tick.connect(self.on_value)

    def terminate(self):
        self.instant_timer.stop()
        self.processing_timer.stop()

        Settings.set_for_channel(
            self.channel, 'processing_rate', self.processing_rate)
        Settings.set_for_channel(
            self.channel, 'direct_processing_size', self.direct_processing_size)
        Settings.set_for_channel(
            self.channel, 'fft_processing_size', self.fft_processing_size)
        Settings.set_for_channel(
            self.channel, 'direct_x_converted', self.direct_x_converted)
        Settings.set_for_channel(
            self.channel, 'fft_x_converted', self.fft_x_converted)


class ProcessorManager:
    def __init__(self):
        self.threads: list[QtCore.QThread] = []
        self.processors: list[Processor] = []

    def create(self, channel: str) -> Processor:
        thread = QtCore.QThread()
        processor = Processor(channel)

        self.threads.append(thread)
        self.processors.append(processor)

        processor.moveToThread(thread)
        thread.start()
        return processor

    def terminate(self):
        for processor in self.processors:
            processor.terminate()

        for thread in self.threads:
            thread.terminate()
