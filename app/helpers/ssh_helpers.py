from netmiko import ConnectHandler
from app.helpers.textfsm_function import textfsm_extractor

class CiscoIOSSSH:
    def __init__(self, device, user):
        self.ip = device.ip
        self.port = device.port
        self.device_type = device.netmiko_driver
        self.username = user.username
        self.password = user.password
        self.secret = user.secret
        self.device_id = device.id
        
        self.netmiko_credentials = {
            "device_type": self.device_type,
            "ip": self.ip,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "secret": self.secret
        }

        self.ssh_session = ConnectHandler(**self.netmiko_credentials)
        self.ssh_session.enable()

    def show_mac_address_table(self, command="show mac address-table"):
        output = self.ssh_session.send_command(command)
        filtered_output = textfsm_extractor("cisco_ios_show_mac_address_table.template", output)
        for index, entry in enumerate(filtered_output):
            filtered_output[index]["device_id"] = self.device_id
        return filtered_output

    def show_interfaces(self, command="show interfaces"):
        output = self.ssh_session.send_command(command)
        filtered_output = textfsm_extractor("cisco_ios_show_interfaces.template", output)
        for index, entry in enumerate(filtered_output):
            filtered_output[index]["device_id"] = self.device_id
        return filtered_output