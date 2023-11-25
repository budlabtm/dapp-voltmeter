from PyQt6 import QtCore, QtWidgets, QtGui
from pyqtgraph import PlotWidget, mkPen, PlotItem
from .settings import Settings

FONT_PRIMARY = QtGui.QFont('Arial', 15, 700)
FONT_SECONDARY = QtGui.QFont('Arial', 12, 400)


class FormatLabel(QtWidgets.QLabel):
    def __init__(self, text: str, font: QtGui.QFont, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.text = text
        self.draw(font)

    def draw(self, font):
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.setText(self.text)

    def format(self, *args):
        self.setText(self.text % args)


class Selector(QtWidgets.QWidget):
    def __init__(self, name: str, value_range: range, value_default: int, font: QtGui.QFont, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.label = QtWidgets.QLabel(name, self)
        self.selector = QtWidgets.QSpinBox(self)
        self.draw(value_range, value_default, font)

        self.valueChanged = self.selector.valueChanged

    def draw(self, value_range: range, value_default: int, font: QtGui.QFont):
        self.label.setFont(font)
        self.selector.setMinimum(value_range.start)
        self.selector.setMaximum(value_range.stop)
        self.selector.setSingleStep(value_range.step)
        self.selector.setValue(value_default)
        self.selector.lineEdit().setReadOnly(True)

        layout = QtWidgets.QHBoxLayout()

        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.label)
        layout.addWidget(self.selector)

        self.setLayout(layout)

    def get_value(self):
        return self.selector.value()


class Chart(PlotWidget):
    def __init__(self,
                 x_invert: bool,
                 y_log_mode_default: bool,
                 x_view_range_default: range,
                 y_view_range_default: range,
                 parent: QtWidgets.QWidget
                 ) -> None:
        super().__init__(parent)
        self.curve = self.getPlotItem().plot([0], [0])
        self.draw(x_invert, y_log_mode_default, x_view_range_default, y_view_range_default)

    def draw(self, x_invert, y_log_mode_default, x_view_range_default, y_view_range_default):
        self.setBackground((251, 251, 251))
        self.curve.setPen(mkPen(color=(98, 130, 181)))
        self.getPlotItem().getViewBox().invertX(x_invert)
        self.getPlotItem().setLogMode(False, y_log_mode_default)
        self.getPlotItem().showGrid(True, True)
        self.getPlotItem().showAxis('top', True)
        self.getPlotItem().showAxis('right', True)
        self.getPlotItem().getAxis('top').setStyle(tickLength=0, showValues=False)
        self.getPlotItem().getAxis('right').setStyle(tickLength=0, showValues=False)
        self.getPlotItem().setXRange(x_view_range_default[0], x_view_range_default[1], 0)
        self.getPlotItem().setYRange(y_view_range_default[0], y_view_range_default[1], 0)

    def get_view_range(self):
        return self.getPlotItem().viewRange()

    def set_label(self, side, text):
        self.getPlotItem().setLabel(side, text)

    def set_bottom_label(self, text):
        self.set_label('bottom', text)

    def set_y_log_mode(self, mode: bool):
        self.getPlotItem().setLogMode(False, mode)

    def set_data(self, x, y):
        self.curve.setData(x, y)


class Tab(QtWidgets.QWidget):
    processingSizeChanged: QtCore.pyqtSignal
    xConvertedStateChanged: QtCore.pyqtSignal

    def __init__(self, processing_range_default: int, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.processing_size_selector = Selector(
            "Processing size",
            Settings.get_range('processing_size_range'),
            processing_range_default,
            FONT_SECONDARY,
            self
        )
        self.convert_x_checkbox = QtWidgets.QCheckBox('Convert X')

    def get_processing_size(self):
        return self.processing_size_selector.get_value()


class DirectTab(Tab):
    processingSizeChanged = QtCore.pyqtSignal(int)
    xConvertedStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self,
                 processing_range_default: int,
                 x_view_range_default,
                 y_view_range_default,
                 parent: QtWidgets.QWidget
                 ) -> None:
        super().__init__(processing_range_default, parent)
        self.chart = Chart(True, False, x_view_range_default, y_view_range_default, self)
        self.mean_label = FormatLabel("Mean: %.2fkV", FONT_SECONDARY, self)
        self.deviation_label = FormatLabel("Std. dev: %.2fkV", FONT_SECONDARY, self)
        self.draw()

        self.processing_size_selector.valueChanged.connect(
            lambda: self.processingSizeChanged.emit(self.get_processing_size())
        )
        self.convert_x_checkbox.stateChanged.connect(
            lambda: self.xConvertedStateChanged.emit(self.convert_x_checkbox.isChecked())
        )

    def draw(self):
        self.chart.set_label("left", "U, kV")

        info_widget = QtWidgets.QWidget(self)
        info_layout = QtWidgets.QVBoxLayout(info_widget)

        info_layout.addWidget(self.mean_label)
        info_layout.addWidget(self.deviation_label)
        info_layout.addWidget(self.processing_size_selector)
        info_layout.addWidget(self.convert_x_checkbox)
        info_layout.addStretch(1)
        info_layout.setSpacing(10)

        info_widget.setLayout(info_layout)
        info_widget.setMinimumWidth(150)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.chart)
        layout.addWidget(info_widget)

        self.setLayout(layout)

    def get_chart_view_range(self):
        return self.chart.get_view_range()

    def set_chart_data(self, x, y):
        self.chart.set_data(x, y)

    def set_mean(self, mean):
        self.mean_label.format(mean)

    def set_deviation(self, deviation):
        self.deviation_label.format(deviation)

    def set_label(self, label):
        self.chart.set_bottom_label(label)


class FftTab(Tab):
    processingSizeChanged = QtCore.pyqtSignal(int)
    xConvertedStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self,
                 processing_range_default: int,
                 y_log_mode_default: bool,
                 x_view_range_default,
                 y_view_range_default,
                 parent: QtWidgets.QWidget
                 ) -> None:
        super().__init__(processing_range_default, parent)
        self.chart = Chart(False, y_log_mode_default, x_view_range_default, y_view_range_default, self)
        self.y_log_mode_checkbox = QtWidgets.QCheckBox("Log Y", self)
        self.draw(y_log_mode_default)

        self.processing_size_selector.valueChanged.connect(
            lambda: self.processingSizeChanged.emit(self.get_processing_size()))
        self.y_log_mode_checkbox.stateChanged.connect(
            lambda: self.chart.set_y_log_mode(self.y_log_mode_checkbox.isChecked()))
        self.convert_x_checkbox.stateChanged.connect(
            lambda: self.xConvertedStateChanged.emit(self.convert_x_checkbox.isChecked())
        )

    def draw(self, y_log_mode_default):
        self.chart.set_label('left', 'U, kV')
        self.y_log_mode_checkbox.setChecked(y_log_mode_default)

        info_widget = QtWidgets.QWidget(self)
        info_layout = QtWidgets.QVBoxLayout(info_widget)

        info_layout.addWidget(self.y_log_mode_checkbox)
        info_layout.addWidget(self.convert_x_checkbox)
        info_layout.addWidget(self.processing_size_selector)
        info_layout.addStretch(1)
        info_widget.setLayout(info_layout)
        info_widget.setMinimumWidth(150)

        layout = QtWidgets.QHBoxLayout(self)

        layout.addWidget(self.chart)
        layout.addWidget(info_widget)
        self.setLayout(layout)

    def get_chart_view_range(self):
        return self.chart.get_view_range()

    def get_y_log_mode(self):
        return self.y_log_mode_checkbox.isChecked()

    def set_chart_data(self, x, y):
        self.chart.set_data(x, y)

    def set_label(self, label):
        self.chart.set_bottom_label(label)


class StreamWidget(QtWidgets.QWidget):
    processingRateChanged = QtCore.pyqtSignal(int)
    currentTabChanged = QtCore.pyqtSignal(int)

    def __init__(self, channel: str, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.channel = channel
        self.channel_label = FormatLabel(Settings.get_for_channel(channel, 'title'), FONT_PRIMARY, self)
        self.processing_rate_selector = Selector(
            "Processing rate",
            Settings.get_range('processing_rate_range'),
            int(Settings.get_for_channel(channel, 'processing_rate')),
            FONT_SECONDARY,
            self
        )
        self.instant_label = FormatLabel("Instant: %.2fkV", FONT_PRIMARY, self)
        self.tab = QtWidgets.QTabWidget(self)
        self.direct_tab = DirectTab(
            int(Settings.get_for_channel(channel, 'direct_processing_size')),
            Settings.get_view_range(channel + '/direct_x_view_range'),
            Settings.get_view_range(channel + '/direct_y_view_range'),
            self
        )
        self.fft_tab = FftTab(
            int(Settings.get_for_channel(channel, 'fft_processing_size')),
            str(Settings.get_for_channel(channel, 'fft_y_log_mode')) == 'true',
            Settings.get_view_range(channel + '/fft_x_view_range'),
            Settings.get_view_range(channel + '/fft_y_view_range'),
            self
        )
        self.direct_tab.convert_x_checkbox.setChecked(Settings.get_for_channel(channel, 'direct_x_converted') == 'true')
        self.fft_tab.convert_x_checkbox.setChecked(Settings.get_for_channel(channel, 'fft_x_converted') == 'true')
        self.draw()

        self.processing_rate_selector.valueChanged.connect(
            lambda: self.processingRateChanged.emit(self.processing_rate_selector.get_value())
        )
        self.tab.currentChanged.connect(lambda: self.currentTabChanged.emit(self.tab.currentIndex()))
        self.fftProcessingSizeChanged = self.fft_tab.processingSizeChanged
        self.fftXConvertedStateChanged = self.fft_tab.xConvertedStateChanged
        self.directProcessingSizeChanged = self.direct_tab.processingSizeChanged
        self.directXConvertedStateChanged = self.direct_tab.xConvertedStateChanged

    def draw(self):
        self.tab.addTab(self.direct_tab, "U")
        self.tab.addTab(self.fft_tab, "FFT")

        top_bar_widget = QtWidgets.QWidget(self)
        top_bar_layout = QtWidgets.QHBoxLayout()

        top_bar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        top_bar_layout.setSpacing(20)
        top_bar_layout.addWidget(self.channel_label)
        top_bar_layout.addWidget(self.processing_rate_selector)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.instant_label)
        top_bar_widget.setLayout(top_bar_layout)

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(top_bar_widget)
        layout.addWidget(self.tab)
        self.setLayout(layout)

    def set_direct_label(self, label):
        self.direct_tab.set_label(label)

    def set_fft_label(self, label):
        self.fft_tab.set_label(label)

    def set_instant_value(self, value):
        self.instant_label.format(value)

    def set_direct_chart_data(self, x, y):
        self.direct_tab.set_chart_data(x, y)

    def set_mean(self, mean):
        self.direct_tab.set_mean(mean)

    def set_deviation(self, deviation):
        self.direct_tab.set_deviation(deviation)

    def set_fft_chart_data(self, x, y):
        self.fft_tab.set_chart_data(x, y)

    def terminate(self):
        dvr = self.direct_tab.get_chart_view_range()
        fvr = self.fft_tab.get_chart_view_range()

        Settings.set_for_channel(self.channel, 'direct_x_view_range', '{}:{}'.format(dvr[0][0], dvr[0][1]))
        Settings.set_for_channel(self.channel, 'direct_y_view_range', '{}:{}'.format(dvr[1][0], dvr[1][1]))
        Settings.set_for_channel(self.channel, 'fft_x_view_range', '{}:{}'.format(fvr[0][0], fvr[0][1]))
        Settings.set_for_channel(self.channel, 'fft_y_view_range', '{}:{}'.format(fvr[1][0], fvr[1][1]))

        Settings.set_for_channel(self.channel, 'fft_y_log_mode', self.fft_tab.get_y_log_mode())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout()
        self.setGeometry(0, 0, int(Settings.get('window_width')), int(Settings.get('window_height')))
        self.setWindowTitle(Settings.get('window_title'))

    def show(self):
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        super().show()

    def add_stream_widget(self, widget: StreamWidget):
        self.layout.addWidget(widget)
