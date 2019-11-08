import paho.mqtt.client as mqtt
from iot_devices import Magnometer
from config import IoTConfig
import h5py


def test_mqtt():
    config = IoTConfig()

    client = mqtt.Client()
    topic = config.get_setting(name='magnetometer', header='device_topic')
    mag = Magnometer(topic=topic)
    mag.device_setup()

    sub = config.get_setting(name='topic_subscription')
    localhost = config.get_setting(name='host')
    port = config.get_setting(name='port')

    def on_connect(mqtt_client, obj, flags, rc):
        mqtt_client.subscribe(sub)
        print("connected with ", rc)

    def on_message(mqtt_client, obj, msg):
        try:
            print(msg.topic, msg.payload)
            print(msg.topic == mag.topic, (msg.topic, mag.topic))
        except Exception as err:
            print(err)

    client = mqtt.Client()
    client.on_connect = on_connect
    print(mag.topic, mag.on_message)
    # client.message_callback_add('#', mag.on_message)
    client.on_message = on_message
    client.connect(localhost, int(port))
    client.loop_forever()


def test_file_status(path):
    while 1:
        try:
            with h5py.File(path, 'r') as f:
                f.keys()
                print("File Available")
        except IOError:
            print("File Closed")


test_file_status(path='example_backups/magnetometer.hd5')