from PyQt6 import QtCore, QtWidgets
from .stream import Stream
from .processor import ProcessorManager
from .view import StreamWidget


class Controller(QtCore.QObject):
    def __init__(self) -> None:
        super().__init__()
        self.stream = Stream()

        while not self.stream.client.is_connected():
            pass

        self.processorManager = ProcessorManager()
        self.widgets: list[StreamWidget] = []

    def create_widget(self, channel, parent: QtWidgets.QWidget):
        source = self.stream.branch(channel)
        processor = self.processorManager.create(channel)
        widget = StreamWidget(channel, parent)

        source.tick.connect(processor.on_value)

        processor.updateInstant.connect(widget.set_instant_value)
        processor.updateMean.connect(widget.set_mean)
        processor.updateDeviation.connect(widget.set_deviation)
        processor.updateDirectChartData.connect(widget.set_direct_chart_data)
        processor.updateFFTChartData.connect(widget.set_fft_chart_data)
        processor.updateDirectLabel.connect(widget.set_direct_label)
        processor.updateFFTLabel.connect(widget.set_fft_label)

        widget.processingRateChanged.connect(processor.set_processing_rate)
        widget.currentTabChanged.connect(processor.set_current_tab)
        widget.directProcessingSizeChanged.connect(processor.set_direct_processing_size)
        widget.fftProcessingSizeChanged.connect(processor.set_fft_processing_size)
        widget.directXConvertedStateChanged.connect(processor.set_direct_x_converted)
        widget.fftXConvertedStateChanged.connect(processor.set_fft_x_converted)

        self.widgets.append(widget)
        return widget

    def terminate(self):
        self.stream.terminate()
        self.processorManager.terminate_all()

        for widget in self.widgets:
            widget.terminate()
