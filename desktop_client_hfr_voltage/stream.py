from PyQt6 import QtCore
from .settings import Settings
import paho.mqtt.client as mqtt


class Source(QtCore.QObject):
    tick = QtCore.pyqtSignal(float)

    def __init__(self, channel: str, client: mqtt.Client) -> None:
        super().__init__()
        self.channel = channel
        self.client = client

        self.factor = float(Settings.get_for_channel(channel, 'factor'))
        self.topic = Settings.get_for_channel(self.channel, 'topic')

        self.client.message_callback_add(self.topic, self.on_message)
        self.client.subscribe(self.topic)

    def on_message(self, _id, _data, message):
        self.tick.emit(float(message.payload) * self.factor)


class Stream(QtCore.QObject):
    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()
    connectionFailed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.client = mqtt.Client()
        self.sources: list[Source] = []

        self.client.username_pw_set(Settings.get(
            'MQTT/username'), Settings.get('MQTT/password'))
        self.client.on_connect = lambda *argv: self.connected.emit()
        self.client.on_connect_fail = lambda *argv: self.connectionFailed.emit()
        self.client.on_disconnect = lambda *argv: self.disconnected.emit()

        self.client.loop_start()
        self.client.connect(Settings.get('MQTT/host'))

    def branch(self, channel: str) -> Source:
        source = Source(channel, self.client)
        self.sources.append(source)
        return source

    def clear(self):
        for source in self.sources:
            self.client.message_callback_remove(source.topic)
            self.sources.remove(source)

    def reconnect(self):
        self.client.reconnect()

    def terminate(self):
        self.client.loop_stop()
        self.client.disconnect()
