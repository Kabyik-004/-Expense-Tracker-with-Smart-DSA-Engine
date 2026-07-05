from datetime import datetime, timezone

from flask_jwt_extended import get_jwt_identity

from app.statement_import.service import ImportService
from app.statement_import.parser import get_supported_banks
from app.utils.responses import success_response, error_response


def handle_upload(request):
    if "file" not in request.files:
        return error_response("No file provided in the request", 400)

    file = request.files["file"]

    validation = ImportService.validate_file(file)
    if not validation["valid"]:
        return error_response(validation["error"], 400)

    result = ImportService.store_temp_file(file, validation["filename"])

    metadata = {
        "id": result["id"],
        "filename": validation["filename"],
        "file_type": validation["file_type"],
        "file_size": validation["file_size"],
        "stored_path": result["stored_path"],
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

    return success_response(data=metadata, message="File uploaded successfully", status_code=201)


def handle_preview(request):
    data = request.get_json(silent=True) or {}
    file_id = data.get("file_id")
    if not file_id:
        return error_response("file_id is required", 400)

    user_id = get_jwt_identity()
    result = ImportService.parse_and_preview(file_id, user_id=user_id)
    if "error" in result:
        return error_response(result["error"], 404)

    return success_response(data=result, message="Preview generated")


def handle_confirm(request):
    data = request.get_json(silent=True) or {}
    file_id = data.get("file_id")
    transactions = data.get("transactions", [])

    if not transactions:
        return error_response("No transactions provided", 400)

    user_id = get_jwt_identity()
    result = ImportService.execute_import(
        user_id=user_id,
        transactions=transactions,
        file_id=file_id,
        filename=data.get("filename"),
        file_type=data.get("file_type"),
    )

    if not result.get("success"):
        return error_response(result.get("error", "Import failed"), 500)

    return success_response(data=result, message="Import completed successfully")


def handle_history():
    return error_response("Not implemented", 501)


def handle_detail(statement_id):
    return error_response("Not implemented", 501)


def handle_delete(statement_id):
    return error_response("Not implemented", 501)


def handle_supported_banks():
    banks = get_supported_banks()
    return success_response(data={"banks": banks})
