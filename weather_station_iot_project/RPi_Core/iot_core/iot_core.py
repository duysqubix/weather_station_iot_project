import paho.mqtt.client as mqtt
import mqtt as mqtt
import iot_devices as devices
from config import IoTConfig

if __name__ == '__main__':
    config = IoTConfig()

    devices = [
        devices.Magnometer(topic=config.get_device('magnometer')),
        devices.Geiger(topic=config.get_device('gieger')),
        devices.WTX520(topic=config.get_device('wtx520'))
    ]

    iot = mqtt.MQTT()
    iot.add(devices)
    iot.initialize_devices()
    print("Beginning main loop")
    iot.main_loop()
