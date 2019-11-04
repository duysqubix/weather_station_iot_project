import paho.mqtt.client as mqtt
from iot_devices import IoTDevice
from config import IoTConfig


class MQTT:
    devices = list()

    def __init__(self, *args, **kwargs):
        self.client = mqtt.Client("", True, None, mqtt.MQTTv311)
        self.config = IoTConfig()

    def main_loop(self):
        self._init_mqtt()
        self.client.loop_forever()

    def add(self, iot_devices):
        if isinstance(iot_devices, (list, tuple)):
            for device in iot_devices:
                assert isinstance(device, IoTDevice)
                self.client.message_callback_add(device.topic,
                                                 device.on_message)

                self.devices.append(device)

        else:
            assert isinstance(iot_devices, IoTDevice)
            self.client.message_callback_add(iot_devices.topic,
                                             iot_devices.on_message)

            self.devices.append(iot_devices)

    def summary(self):
        print("Devices Added:")
        summary_ = ""
        for device in self.devices:
            summary_ += "\tName: {} Topic: {}\n".format(
                device.name.split('/')[-1], device.topic)

        print(summary_)

    def initialize_devices(self):
        for device in self.devices:
            device.device_setup()

    def _init_mqtt(self):
        port = self.config.get_setting(name='port')
        keepalive = self.config.get_setting(name='keepalive')
        host = self.config.get_setting(name='host')

        self.client.on_connect = self._on_connect
        self.client.connect(str(host), int(port), int(keepalive))

    def _on_connect(self, client, userdata, flags, rc):
        topics = self.config.get_setting(name='topic_subscription')
        print("Connected with result code ", rc)
        print("Subscribing to topics: {}".format(topics))

        self.client.subscribe(str(topics))
