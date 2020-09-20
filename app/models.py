from app import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    secret = db.Column(db.String)
    devices = db.relationship("Device", backref="user", lazy="dynamic")

    def __repr__(self):
        return "<CMAD User {}>".format(self.username)

    def as_dict(self, show_password=True):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password if show_password else "--hidden--",
            "secret": self.secret,
            "devices": [_device.id for _device in self.devices]
        }

class Device(db.Model):
    __tablename__ = "device"

    id = db.Column(db.Integer, primary_key=True)
    friendly_name = db.Column(db.String)
    ip = db.Column(db.String)
    port = db.Column(db.Integer)
    netmiko_driver = db.Column(db.String)
    authentication_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    mac_entries = db.relationship("MacEntry", backref="device", lazy="dynamic")
    interfaces = db.relationship("Interface", backref="device", lazy="dynamic")

    def __repr__(self):
        return "<CMAD Device {}>".format(self.id)

    def as_dict(self):
        return {
            "id": self.id,
            "friendly_name": self.friendly_name,
            "ip": self.ip,
            "port": self.port,
            "netmiko_driver": self.netmiko_driver,
            "authentication_user": self.authentication_user,
            "mac_entries": [{"address": mac.address, "port": mac.port} for mac in self.mac_entries]
        }

    def as_dict_basic(self):
        return {
            "id": self.id,
            "friendly_name": self.friendly_name,
            "ip": self.ip,
            "port": self.port
        }

class MacEntry(db.Model):
    __tablename__ = "mac_entry"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("device.id"))
    vlan = db.Column(db.Integer)
    address = db.Column(db.String)
    address_type = db.Column(db.String)
    port = db.Column(db.String)

    def __repr__(self):
        return "<CMAD MacEntry {}>".format(self.address)

    def as_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "vlan": self.vlan,
            "address": self.address,
            "address_type": self.address_type,
            "port": self.port
        }

class Interface(db.Model):
    __tablename__ = "interface"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("device.id"))
    address = db.Column(db.String)
    bandwidth = db.Column(db.String)
    bia = db.Column(db.String)
    crc = db.Column(db.String)
    delay = db.Column(db.String)
    description = db.Column(db.String)
    duplex = db.Column(db.String)
    encapsulation = db.Column(db.String)
    hardware_type = db.Column(db.String)
    interface = db.Column(db.String)
    ip_address = db.Column(db.String)
    mtu = db.Column(db.String)
    speed = db.Column(db.String)

    def __repr__(self):
        return "<CMAD Interface {}>".format(self.id)

    def as_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "address": self.address,
            "bandwidth": self.bandwidth,
            "bia": self.bia,
            "crc": self.crc,
            "delay": self.delay,
            "description": self.description,
            "duplex": self.duplex,
            "encapsulation": self.encapsulation,
            "hardware_type": self.hardware_type,
            "interface": self.interface,
            "ip_address": self.ip_address,
            "mtu": self.mtu,
            "speed": self.speed
        }


"""
    "abort": "",
    "address": "0016.c886.51c0",
    "bandwidth": "1000000 Kbit",
    "bia": "0016.c886.51c0",
    "crc": "0",
    "delay": "10 usec",
    "description": "",
    "duplex": "",
    "encapsulation": "ARPA",
    "hardware_type": "EtherSVI",
    "input_errors": "0",
    "input_packets": "0",
    "input_rate": "0",
    "interface": "Vlan1",
    "ip_address": "",
    "last_input": "never",
    "last_output": "never",
    "last_output_hang": "never",
    "link_status": "up",
    "media_type": "",
    "mtu": "1500",
    "output_errors": "",
    "output_packets": "0",
    "output_rate": "0",
    "protocol_status": "down",
    "queue_strategy": "fifo",
    "speed": ""
"""