from flask import Blueprint, request
from app.views import api_users
from app.models import Device, User, MacEntry
from app import db
from app.helpers import json_responses, ssh_helpers, dbfunctions

bp = Blueprint("api_devices", __name__, url_prefix="/api/v1/devices")

@bp.route("/", methods=["GET"])
def api_devices():
    devices = Device.query.all()

    return json_responses.generic_response(False, [device.as_dict() for device in devices if devices])

@bp.route("/<int:id>", methods=["GET"])
def api_get_device(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    return json_responses.generic_response(False, [device.as_dict()])

@bp.route("/", methods=["POST"])
def api_create_device():
    if not request.is_json:
        return json_responses.invalid_json()

    data = request.get_json()

    check_fields = json_responses.check_fields(["friendly_name", "ip", "port", "netmiko_driver", "authentication_user"], data)
    if check_fields["error"]:
        return check_fields

    check_device = dbfunctions.check_device_exist_ip(data["ip"])
    if check_device:
        return json_responses.generic_response(True, "device with IP {} already exist.".format(data["ip"]))

    check_driver = dbfunctions.check_netmiko_driver(data["netmiko_driver"])
    if not check_driver:
        return json_responses.generic_response(True, "{} is an invalid netmiko_driver. Please see Netmiko supported drivers at: https://github.com/ktbyers/netmiko".format(data["netmiko_driver"]))

    check_user = dbfunctions.check_user_exist(data["authentication_user"])
    if not check_user:
        return json_responses.generic_response(True, "user {} does not exist.".format(data["authentication_user"]))

    try:
        device = Device(**data)
        db.session.add(device)
        db.session.commit()
    except Exception as error:
        return json_responses.generic_response(True, error)

    return json_responses.generic_response(False, [device.as_dict()])

@bp.route("/<int:id>", methods=["DELETE"])
def api_delete_device(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    try:
        db.session.delete(device)
        db.session.commit()
    except Exception as error:
        return json_responses.generic_response(True, error)

    return json_responses.generic_response(False, "Successfully deleted device {}.".format(id))

@bp.route("/<int:id>", methods=["PATCH"])
def api_update_device(id):
    if not request.is_json:
        return json_responses.invalid_json()

    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    data = request.get_json()

    try:
        for k,v in data.items():
            if k == "netmiko_driver":
                check_driver = dbfunctions.check_netmiko_driver(v)
                if not check_driver:
                    return json_responses.generic_response(True, "Invalid netmiko_driver {}".format(v))
            setattr(device, k, v)
    except Exception as error:
        return json_responses.generic_response(True, error)

    db.session.commit()
    return json_responses.generic_response(False, [device.as_dict()])

@bp.route("/<int:id>/get_mac_table", methods=["GET"])
def api_get_device_macs(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    user = User.query.get(device.authentication_user)

    ssh_session = None
    try:
        ssh_session = ssh_helpers.CiscoIOSSSH(device, user)
    except Exception as error:
        return json_responses.generic_response(True, error)

    mac_entries = ssh_session.show_mac_address_table()
    if not mac_entries:
        return json_responses.generic_response(False, "No MAC Entries found to add into database...")

    cleanup_macs_in_database = [mac.address for mac in dbfunctions.get_device_macs(device.id)]

    added_macs = []
    for entry in mac_entries:
        check_mac_exist = dbfunctions.check_mac_exist_address(entry["address"])
        if not check_mac_exist:
            mac = MacEntry(**entry)
            db.session.add(mac)
            added_macs.append(mac.as_dict())
        else:
            for k,v in entry.items(): # Update existing MAC Addresses
                setattr(check_mac_exist, k, v)
            added_macs.append(check_mac_exist.as_dict())
            del cleanup_macs_in_database[cleanup_macs_in_database.index(entry["address"])]

    for stale_mac in cleanup_macs_in_database:
        stale_mac = dbfunctions.check_mac_exist_address(stale_mac)
        if not stale_mac:
            continue
        db.session.delete(stale_mac)
        print("Deleting Stale MAC {}".format(stale_mac.address))
    db.session.commit()

    return json_responses.generic_response(False, added_macs)