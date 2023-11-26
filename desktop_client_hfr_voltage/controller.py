from PyQt6 import QtCore
from .stream import Stream
from .processor import ProcessorManager
from .view import StreamWidget, MainWindow


class Controller(QtCore.QObject):
    def __init__(self) -> None:
        super().__init__()
        self.stream = Stream()
        self.processorManager = ProcessorManager()
        self.view = MainWindow()

        self.stream.connected.connect(self.on_connect)
        self.stream.connectionFailed.connect(self.on_connection_fail)
        self.stream.disconnected.connect(self.on_disconnect)

        self.create_stream('C0')
        self.create_stream('C1')
        self.view.show()

    def on_connect(self):
        self.view.set_connection_status('Connected.')
        self.stream.clear()
        self.resource()

    def on_connection_fail(self):
        self.view.set_connection_status(
            'Failed. Check credentials and host status.')

    def on_disconnect(self):
        self.view.set_connection_status('Disconnected. Reconnecting...')
        self.stream.reconnect()

    def create_stream(self, channel):
        processor = self.processorManager.create(channel)
        widget = StreamWidget(channel, self.view)

        processor.updateInstant.connect(widget.set_instant_value)
        processor.updateMean.connect(widget.set_mean)
        processor.updateDeviation.connect(widget.set_deviation)
        processor.updateDirectChartData.connect(widget.set_direct_chart_data)
        processor.updateFFTChartData.connect(widget.set_fft_chart_data)
        processor.updateDirectLabel.connect(widget.set_direct_label)
        processor.updateFFTLabel.connect(widget.set_fft_label)

        widget.processingRateChanged.connect(processor.set_processing_rate)
        widget.currentTabChanged.connect(processor.set_current_tab)
        widget.directProcessingSizeChanged.connect(
            processor.set_direct_processing_size)
        widget.fftProcessingSizeChanged.connect(
            processor.set_fft_processing_size)
        widget.directXConvertedStateChanged.connect(
            processor.set_direct_x_converted)
        widget.fftXConvertedStateChanged.connect(processor.set_fft_x_converted)

        self.view.add_stream_widget(widget)

    def resource(self):
        for processor in self.processorManager.processors:
            processor.attach_source(self.stream.branch(processor.channel))

    def terminate(self):
        self.view.terminate()
        self.processorManager.terminate()
        self.stream.terminate()
