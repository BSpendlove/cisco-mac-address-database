from app import db

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    secret = db.Column(db.String)
    devices = db.relationship("Device", backref="user", lazy='dynamic')

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
    mac_entries = db.relationship("MacEntry", backref="device", lazy='dynamic')

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