from PyQt6 import QtCore
from settings import Settings
import paho.mqtt.client as mqtt


class Source(QtCore.QObject):
    tick = QtCore.pyqtSignal(float)

    def __init__(self, channel: str, client: mqtt.Client) -> None:
        super().__init__()
        self.factor = float(Settings.get_for_channel(channel, 'factor'))
        
        client.message_callback_add(Settings.get_for_channel(channel, 'topic'), self.on_message)
        client.subscribe(Settings.get_for_channel(channel, 'topic'))

    def on_message(self, _id, _data, message):
        self.tick.emit(float(message.payload) * self.factor)
        
        
class Stream:
    def __init__(self):
        self.running = True
        self.client = mqtt.Client()
        self.client.username_pw_set(Settings.get('MQTT/username'), Settings.get('MQTT/password'))
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_start()
        self.client.connect(Settings.get('MQTT/host'))
        
    def branch(self, channel: str) -> Source:
        return Source(channel, self.client)

    def terminate(self):
        self.client.loop_stop()
        self.running = False
        self.client.disconnect()

    def on_disconnect(self, *args):
        if self.running:
            self.client.reconnect()
