from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.activity_controller import list_activities

activity_bp = Blueprint("activity", __name__)


@activity_bp.route("/activity", methods=["GET"])
@jwt_required()
def get_activities():
    return list_activities()
