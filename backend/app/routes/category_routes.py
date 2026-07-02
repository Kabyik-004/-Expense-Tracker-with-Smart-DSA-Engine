from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers.category_controller import list_categories

category_bp = Blueprint("categories", __name__)


@category_bp.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    return list_categories()