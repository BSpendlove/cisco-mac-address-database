from flask import Blueprint, request
from app.models import User
from app import db
from app.helpers import json_responses, dbfunctions

bp = Blueprint("api_users", __name__, url_prefix="/api/v1/users")

@bp.route("/", methods=["GET"])
def api_users():
    users = User.query.all()

    return json_responses.generic_response(False, [user.as_dict() for user in users if users])

@bp.route("/<int:id>", methods=["GET"])
def api_get_user(id):
    user = dbfunctions.check_user_exist(id)
    if not user:
        return json_responses.generic_response(True, "user {} does not exist.".format(id))

    return json_responses.generic_response(False, [user.as_dict()])

@bp.route("/", methods=["POST"])
def api_create_user():
    if not request.is_json:
        return json_responses.invalid_json()

    data = request.get_json()

    check_fields = json_responses.check_fields(["username", "password"], data)
    if check_fields["error"]:
        return check_fields

    check_user = dbfunctions.check_user_exist_username(data["username"])
    if check_user:
        return json_responses.generic_response(True, "user {} already exist.".format(data["username"]))

    try:
        user = User(**data)
        db.session.add(user)
        db.session.commit()
    except Exception as error:
        return json_responses.generic_response(True, error)

    return json_responses.generic_response(False, [user.as_dict()])

@bp.route("/<int:id>", methods=["DELETE"])
def api_delete_user(id):
    user = dbfunctions.check_user_exist(id)
    if not user:
        return json_responses.generic_response(True, "user {} does not exist.".format(id))

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as error:
        return json_responses.generic_response(True, error)

    return json_responses.generic_response(False, "Successfully deleted user {}.".format(id))

@bp.route("/<int:id>", methods=["PATCH"])
def api_update_user(id):
    if not request.is_json:
        return json_responses.invalid_json()

    user = dbfunctions.check_user_exist(id)
    if not user:
        return json_responses.generic_response(True, "user {} does not exist.".format(id))

    data = request.get_json()

    try:
        for k,v in data.items():
            setattr(user, k, v)
    except Exception as error:
        return json_responses.generic_response(True, error)

    db.session.commit()
    return json_responses.generic_response(False, [user.as_dict()])