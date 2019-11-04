from backup import BackUp
from config import IoTConfig


class IoTDevice:
    def __init__(self, topic, name=None):
        self.topic = topic
        self.name = name if name is not None else self.topic

        self.config = IoTConfig()
        self.storage_path = self.config.get_setting(name='path',
                                                    header='local_backup')

    def on_message(self, client, userdata, msg):
        pass

    def device_setup(self):
        pass

    def default_print(self, msg):
        if not isinstance(msg, str):
            try:
                msg = str(msg, encoding='utf-8')
            except UnicodeDecodeError as err:
                print(err)

        print("{}:{}".format(self.name, msg))

    def _payload_error(self):
        print("Error delivering payload")


class Magnometer(IoTDevice):
    def device_setup(self):
        # set up back settings
        header = 'magnetometer'
        print(self.storage_path)
        fname = self.config.get_setting(name='backup_name', header=header)

        device_settings = self.config.get_all_settings(header='magnetometer')
        self.backup_h = BackUp(path=self.storage_path,
                               fname=fname,
                               **device_settings)

    def on_message(self, client, userdata, msg):
        try:
            self.default_print(msg.payload)
        except:
            self._payload_error()


class WTX520(IoTDevice):
    def device_setup(self):
        pass

    def on_message(self, client, userdata, msg):
        self.default_print(msg.payload)


class Geiger(IoTDevice):
    def device_setup(self):
        pass

    def on_message(self, client, userdata, msg):
        self.default_print(msg.payload)
