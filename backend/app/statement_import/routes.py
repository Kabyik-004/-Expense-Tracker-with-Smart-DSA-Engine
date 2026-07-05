from flask import request
from flask_jwt_extended import jwt_required

from app.statement_import import import_bp
from app.statement_import.controller import (
    handle_upload,
    handle_preview,
    handle_confirm,
    handle_history,
    handle_detail,
    handle_delete,
    handle_supported_banks,
)


@import_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    return handle_upload(request)


@import_bp.route("/preview", methods=["POST"])
@jwt_required()
def preview():
    return handle_preview(request)


@import_bp.route("/confirm", methods=["POST"])
@jwt_required()
def confirm():
    return handle_confirm(request)


@import_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    return handle_history()


@import_bp.route("/<int:statement_id>", methods=["GET"])
@jwt_required()
def detail(statement_id):
    return handle_detail(statement_id)


@import_bp.route("/<int:statement_id>", methods=["DELETE"])
@jwt_required()
def delete(statement_id):
    return handle_delete(statement_id)


@import_bp.route("/supported-banks", methods=["GET"])
@jwt_required()
def supported_banks():
    return handle_supported_banks()
