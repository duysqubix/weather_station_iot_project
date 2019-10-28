import configparser


class IoTConfig(configparser.ConfigParser):
    config_file_path = "./config.ini"

    def __init__(self):
        super(IoTConfig, self).__init__()
        self.read(self.config_file_path)

    def get_setting(self, name, header='mqtt', evaluate=True):
        try:
            settings = self[header][name]
            return settings if evaluate is False else eval(settings)

        except KeyError as err:
            print(err)

    def get_devices(self, header='device_topic'):
        devices = []
        for device in self[header]:
            devices.append((device, self[header][device]))

        return devices

    def get_device(self, device_name, header='device_topic'):

        try:
            return self[header][device_name]
        except KeyError as err:
            print(err)
    

if __name__ == "__main__":
    config = IoTConfig()
    for sec in config.sections():
        for key in config[sec]:
            print(sec, key, config[sec][key])

    print(config.get_devices())