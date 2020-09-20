from flask import Blueprint, request
from app.models import Device, MacEntry, Interface
from app import db
from app.helpers import json_responses, ssh_helpers, dbfunctions

bp = Blueprint("api_devices", __name__, url_prefix="/api/v1/devices")

# /ssh routes will invoke SSH sessions whereas if you'd like to only filter on the database, remove the relevant /ssh route...
# eg:
#   /api/v1/devices/1/ssh/get_interfaces - Will SSH to the device and create/update interfaces in the database, and return them
#   /api/v1/devices/1/get_interfaces - Will query the database and not invoke any SSH and database CREATE/UPDATE queries. This is just a SELECT query.

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

@bp.route("/<int:id>/ssh/get_interfaces", methods=["GET"])
def api_ssh_get_device_interfaces(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    user = dbfunctions.check_user_exist(device.authentication_user)

    ssh_session = None
    try:
        ssh_session = ssh_helpers.CiscoIOSSSH(device, user)
    except Exception as error:
        return json_responses.generic_response(True, error)

    interfaces = ssh_session.show_interfaces()
    added_interfaces = []
    for entry in interfaces:
        _interface = dbfunctions.create_interface(**entry)
        added_interfaces.append(_interface.as_dict())

    return json_responses.generic_response(False, added_interfaces)

@bp.route("/<int:id>/get_interfaces", methods=["GET"])
def api_get_device_interfaces(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    return json_responses.generic_response(False, [interface.as_dict() for interface in device.interfaces.all()])

@bp.route("/<int:id>/ssh/macs_by_port", methods=["POST"])
def api_ssh_get_device_macs_by_port(id):
    if not request.is_json:
        return json_responses.invalid_json()

    data = request.get_json()

    check_fields = json_responses.check_fields(["port"], data)
    if check_fields["error"]:
        return check_fields

    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    macs = dbfunctions.get_device_macs_by_port(device.id, data["port"])
    return json_responses.generic_response(False, [mac.as_dict() for mac in macs if macs])

@bp.route("/<int:id>/ssh/get_mac_table", methods=["GET"])
def api_ssh_get_device_macs(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    user = dbfunctions.check_user_exist(device.authentication_user)

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
        _mac = dbfunctions.create_mac_address(**entry)
        if _mac.address in cleanup_macs_in_database:
            del cleanup_macs_in_database[cleanup_macs_in_database.index(_mac.address)]
        added_macs.append(_mac.as_dict())

    dbfunctions.cleanup_mac_addresses(cleanup_macs_in_database)

    return json_responses.generic_response(False, added_macs)

@bp.route("/<int:id>/get_mac_table", methods=["GET"])
def api_get_device_macs(id):
    device = dbfunctions.check_device_exist(id)
    if not device:
        return json_responses.generic_response(True, "device {} does not exist.".format(id))

    return json_responses.generic_response(False, [mac.as_dict() for mac in device.mac_entries.all()])
