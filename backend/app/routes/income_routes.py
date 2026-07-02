"""
Income routes — /api/incomes/*
Authenticated CRUD endpoints for income records.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.controllers.income_controller import (
    create_income,
    get_incomes,
    get_income,
    update_income,
    delete_income,
    undo_last_income_operation,
)
from app.utils.responses import error_response

income_bp = Blueprint("incomes", __name__)


@income_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    try:
        return create_income(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@income_bp.route("/", methods=["GET"])
@jwt_required()
def list_incomes():
    return get_incomes()


@income_bp.route("/<int:income_id>", methods=["GET"])
@jwt_required()
def retrieve(income_id):
    return get_income(income_id)


@income_bp.route("/<int:income_id>", methods=["PUT"])
@jwt_required()
def update(income_id):
    try:
        return update_income(income_id, request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@income_bp.route("/<int:income_id>", methods=["DELETE"])
@jwt_required()
def remove(income_id):
    return delete_income(income_id)


@income_bp.route("/undo", methods=["POST"])
@jwt_required()
def undo_income():
    """Undo the last income operation (create, update, or delete)."""
    return undo_last_income_operation(int(get_jwt_identity()))
