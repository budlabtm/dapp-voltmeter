from PyQt6 import QtCore


class Settings:
    def __init__(self):
        pass

    settings = QtCore.QSettings("desktop/client", "hfr/voltage")

    @staticmethod
    def init():
        if Settings.get('reset') is None or int(Settings.get('reset')) == 1:
            Settings.set_default()

    @staticmethod
    def set_default():
        Settings.set('reset', 0)
        Settings.set('window_title', 'Application')
        Settings.set('window_width', 1000)
        Settings.set('window_height', 700)
        Settings.set('processing_rate_range', '1:20:1')
        Settings.set('processing_size_range', '1000:60000:500')

        Settings.set('MQTT/host', 'localhost')
        Settings.set('MQTT/username', 'username')
        Settings.set('MQTT/password', 'password')

        Settings.set('C0/title', 'C0')
        Settings.set('C0/topic', '/test/c0')
        Settings.set('C0/direct_x_converted', 'false')
        Settings.set('C0/fft_x_converted', 'false')
        Settings.set('C0/factor', 1)
        Settings.set('C0/instant_rate', 1)
        Settings.set('C0/processing_rate', 1)
        Settings.set('C0/direct_processing_size', 1000)
        Settings.set('C0/fft_processing_size', 1000)
        Settings.set('C0/fft_y_log_mode', True)
        Settings.set('C0/direct_x_view_range', '0:1000')
        Settings.set('C0/direct_y_view_range', '0:1000')
        Settings.set('C0/fft_x_view_range', '0:0.52')
        Settings.set('C0/fft_y_view_range', '0:1000')

        Settings.set('C1/title', 'C1')
        Settings.set('C1/topic', '/test/c1')
        Settings.set('C0/direct_x_converted', 'false')
        Settings.set('C0/fft_x_converted', 'false')
        Settings.set('C1/factor', 1)
        Settings.set('C1/instant_rate', 1)
        Settings.set('C1/processing_rate', 1)
        Settings.set('C1/direct_processing_size', 1000)
        Settings.set('C1/fft_processing_size', 1000)
        Settings.set('C1/fft_y_log_mode', True)
        Settings.set('C1/direct_x_view_range', '0:1000')
        Settings.set('C1/direct_y_view_range', '0:1000')
        Settings.set('C1/fft_x_view_range', '0:0.52')
        Settings.set('C1/fft_y_view_range', '0:1000')

    @staticmethod
    def set(key: str, value):
        Settings.settings.setValue(key, value)

    @staticmethod
    def set_for_channel(channel: str, key: str, value):
        Settings.set(channel + '/' + key, value)

    @staticmethod
    def get(key: str):
        return Settings.settings.value(key)

    @staticmethod
    def get_for_channel(channel: str, key: str):
        return Settings.get(channel + '/' + key)

    @staticmethod
    def get_range(key: str) -> range:
        tokens = str(Settings.get(key)).split(':')
        return range(
            int(tokens[0]),
            int(tokens[1]),
            int(tokens[2]) if len(tokens) == 3 else 1
        )

    @staticmethod
    def get_view_range(key: str) -> list:
        tokens = str(Settings.get(key)).split(':')
        return [float(tokens[0]), float(tokens[1])]
