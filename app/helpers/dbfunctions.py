from app import db
from app.models import User, Device, MacEntry, Interface
from app.helpers.json_responses import payload_builder
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

def check_interface_exist(id, interface):
    interface = Interface.query.filter_by(device_id=id, interface=interface).first()
    if not interface:
        return None
    return interface

def check_mac_exist(id, address):
    mac = MacEntry.query.filter_by(device_id=id, address=address).first()
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

def create_interface(**kwargs):
    field_mapper = {
        "device_id": "device_id",
        "address": "address",
        "bandwidth": "bandwidth",
        "bia": "bia",
        "crc": "crc",
        "delay": "delay",
        "description": "description",
        "duplex": "duplex",
        "encapsulation": "encapsulation",
        "hardware_type": "hardware_type",
        "interface": "interface",
        "ip_address": "ip_address",
        "mtu": "mtu",
        "speed": "speed"
    }

    check = check_interface_exist(kwargs["device_id"], kwargs["interface"])
    payload = payload_builder(field_mapper, **kwargs)
    if not check:
        # New Interface will be created...
        interface = Interface(**payload)
        db.session.add(interface)
        return interface
    else:
        # Existing interface will be updated...
        for k,v in payload.items():
            setattr(check, k, v)
    db.session.commit()
    return check

def create_mac_address(**kwargs):
    field_mapper = {
        "device_id": "device_id",
        "vlan": "vlan",
        "address": "address",
        "address_type": "address_type",
        "port": "port"
    }

    check = check_mac_exist(kwargs["device_id"], kwargs["address"])
    payload = payload_builder(field_mapper, **kwargs)
    if not check:
        # New MacEntry wil be created...
        mac = MacEntry(**payload)
        db.session.add(mac)
        return mac
    else:
        for k,v in payload.items():
            setattr(check, k, v)

    db.session.commit()
    return check

def cleanup_mac_addresses(addresses):
    for address in addresses:
        stale_mac = check_mac_exist_address(address)
        if not stale_mac:
            continue
        db.session.delete(stale_mac)
    db.session.commit()
