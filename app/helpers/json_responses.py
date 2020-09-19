from netmiko.ssh_dispatcher import CLASS_MAPPER

def generic_response(error, message):
    _json = {
        "error": error
    }

    if isinstance(message, list):
        _json["data"] = message
    else:
        _json["message"] = str(message)

    return _json

def invalid_json():
    return {
        "error": True,
        "message": "Invalid JSON data"
    }

def check_fields(required, data):
    for field in required:
        if not field in data:
            return {
                "error": True,
                "message": "Field {} is missing.".format(field)
            }
    return {
        "error": False
    }