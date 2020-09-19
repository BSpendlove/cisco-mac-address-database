from app import db
from app.models import User, Device, MacEntry
from netmiko.ssh_dispatcher import CLASS_MAPPER

def check_user_exist(id):
    user = User.query.get(id)
    if not user:
        return None
    return user

def check_user_exist_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    return user

def check_device_exist(id):
    device = Device.query.get(id)
    if not device:
        return None
    return device

def check_device_exist_ip(ip_address):
    device = Device.query.filter_by(ip=ip_address).first()
    if not device:
        return None
    return device

def check_mac_exist(id):
    mac = MacEntry.query.get(id)
    if not mac:
        return None
    return mac

def check_mac_exist_address(address):
    mac = MacEntry.query.filter_by(address=address).first()
    if not mac:
        return None
    return mac

def get_device_macs(id):
    device = check_device_exist(id)
    if not device:
        return None
    return device.mac_entries.all()

def get_device_macs_by_port(id, port):
    device = check_device_exist(id)
    if not device:
        return None
    macs = MacEntry.query.filter_by(port=port).all()
    if not macs:
        return None
    return macs

def check_netmiko_driver(driver):
    if driver in CLASS_MAPPER.keys():
        return True
    return False
    