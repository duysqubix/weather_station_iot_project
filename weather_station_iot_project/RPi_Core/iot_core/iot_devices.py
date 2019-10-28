from backup import BackUp
from config import IoTConfig


class IoTDevice:
    def __init__(self, topic, name=None):
        self.topic = topic
        self.name = name if name is not None else self.topic

        self.config = IoTConfig()
        self.storage_path = self.config.get_setting(
            name='path', header='local_backup')

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


class Magnometer(IoTDevice):

    def device_setup(self):
        # set up back settings
        header = 'magnetometer'
        print(self.storage_path)
        fname = self.config.get_setting(name='backup_name', header=header)

        sample_rate = self.config.get_setting(
            name='sample_rate', header=header)

        ndim = self.config.get_setting(name='ndim', header=header)

        attrs = eval(self.config.get_setting(name='attrs', header=header))

        self.backup_h = BackUp(path=self.storage_path,
                               fname=fname, ndim=ndim, attrs=attrs,
                               sample_rate=sample_rate)

    def on_message(self, client, userdata, msg):
        self.default_print(msg.payload)


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
