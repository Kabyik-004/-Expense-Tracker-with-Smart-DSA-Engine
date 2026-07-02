from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.controllers.budget_controller import (
    list_budgets,
    get_budget_status,
    set_budget,
    delete_budget,
)
from app.utils.responses import error_response

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/", methods=["GET"])
@jwt_required()
def get_budgets():
    return list_budgets()


@budget_bp.route("/status", methods=["GET"])
@jwt_required()
def status():
    from flask import request
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    return get_budget_status(month, year)


@budget_bp.route("/", methods=["POST"])
@jwt_required()
def create_budget():
    try:
        return set_budget(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@budget_bp.route("/<int:budget_id>", methods=["DELETE"])
@jwt_required()
def remove_budget(budget_id):
    return delete_budget(budget_id)
