"""
Expense routes — /api/expenses/*
Endpoints: CRUD, filter, search.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.controllers.expense_controller import (
    create_expense,
    list_expenses,
    get_expense,
    update_expense,
    delete_expense,
    sort_expenses_by_field,
    sort_expenses_multi_field,
    undo_last_operation,
    get_undo_stack_status,
    clear_undo_stack,
    get_category_totals,
    get_category_counts,
    get_monthly_totals,
    search_by_title,
    search_by_description,
    search_by_category,
    search_by_id,
    search_by_date,
    search_by_date_range,
)
from app.utils.responses import error_response

expense_bp = Blueprint("expenses", __name__)


@expense_bp.route("/", methods=["POST"])
@jwt_required()
def create():
    try:
        return create_expense(int(get_jwt_identity()), request.get_json())
    except ValidationError as exc:
        return error_response("Validation failed", 400, errors=exc.messages)


@expense_bp.route("/", methods=["GET"])
@jwt_required()
def list_all():
    return list_expenses(int(get_jwt_identity()))


@expense_bp.route("/<int:expense_id>", methods=["GET"])
@jwt_required()
def retrieve(expense_id):
    return get_expense(int(get_jwt_identity()), expense_id)


@expense_bp.route("/<int:expense_id>", methods=["PUT"])
@jwt_required()
def update(expense_id):
    try:
        return update_expense(int(get_jwt_identity()), expense_id, request.get_json())
    except ValidationError as exc:
        return error_response("Validation failed", 400, errors=exc.messages)


@expense_bp.route("/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def remove(expense_id):
    return delete_expense(int(get_jwt_identity()), expense_id)


@expense_bp.route("/sort/single", methods=["GET"])
@jwt_required()
def sort_single():
    """Sort expenses by a single field.
    
    Query parameters:
    - sort_by: amount, date, category_id, title (default: amount)
    - ascending: true/false (default: true)
    """
    sort_by = request.args.get("sort_by", "amount")
    ascending = request.args.get("ascending", "true").lower() == "true"
    return sort_expenses_by_field(int(get_jwt_identity()), sort_by, ascending)


@expense_bp.route("/sort/multi", methods=["POST"])
@jwt_required()
def sort_multi():
    """Sort expenses by multiple fields.
    
    Request body:
    {
        "sort_fields": ["category_id", "amount"],
        "ascending": [true, false]
    }
    """
    try:
        return sort_expenses_multi_field(int(get_jwt_identity()), request.get_json())
    except ValidationError as exc:
        return error_response("Validation failed", 400, errors=exc.messages)


@expense_bp.route("/undo", methods=["POST"])
@jwt_required()
def undo():
    """Undo the last expense operation (create, update, or delete).
    
    Uses LIFO stack - maximum 10 operations per user.
    Time Complexity: O(1)
    """
    return undo_last_operation(int(get_jwt_identity()))


@expense_bp.route("/undo/status", methods=["GET"])
@jwt_required()
def undo_status():
    """Get current undo stack status for the user.
    
    Returns:
    - stack_size: Current number of undo operations
    - max_size: Maximum stack capacity (10)
    - is_empty: Whether undo stack is empty
    - top_operation: Next operation to be undone
    """
    return get_undo_stack_status(int(get_jwt_identity()))


@expense_bp.route("/undo/clear", methods=["POST"])
@jwt_required()
def clear_undo():
    """Clear all undo history for the user."""
    return clear_undo_stack(int(get_jwt_identity()))


@expense_bp.route("/summary/category-totals", methods=["GET"])
@jwt_required()
def summary_category_totals():
    return get_category_totals(int(get_jwt_identity()))


@expense_bp.route("/summary/category-counts", methods=["GET"])
@jwt_required()
def summary_category_counts():
    return get_category_counts(int(get_jwt_identity()))


@expense_bp.route("/summary/monthly-totals", methods=["GET"])
@jwt_required()
def summary_monthly_totals():
    return get_monthly_totals(int(get_jwt_identity()))


# ============================================================================
# SEARCH ROUTES - Linear and Binary Search
# ============================================================================


@expense_bp.route("/search/title", methods=["GET"])
@jwt_required()
def search_title():
    """Linear search for expenses by title.
    
    Query parameters:
    - q: Search query (case-insensitive substring match)
    
    Time Complexity: O(n) - checks all expenses
    """
    query = request.args.get("q", "")
    if not query:
        return error_response("Missing 'q' query parameter", 400)
    
    return search_by_title(int(get_jwt_identity()), query)


@expense_bp.route("/search/description", methods=["GET"])
@jwt_required()
def search_description():
    """Linear search for expenses by description.
    
    Query parameters:
    - q: Search query (case-insensitive substring match)
    
    Time Complexity: O(n)
    """
    query = request.args.get("q", "")
    if not query:
        return error_response("Missing 'q' query parameter", 400)
    
    return search_by_description(int(get_jwt_identity()), query)


@expense_bp.route("/search/category", methods=["GET"])
@jwt_required()
def search_category():
    """Linear search for expenses by category ID.
    
    Query parameters:
    - category_id: Category ID to search for
    
    Time Complexity: O(n)
    """
    category_id = request.args.get("category_id")
    if not category_id:
        return error_response("Missing 'category_id' query parameter", 400)
    
    try:
        category_id = int(category_id)
    except ValueError:
        return error_response("category_id must be an integer", 400)
    
    return search_by_category(int(get_jwt_identity()), category_id)


@expense_bp.route("/search/id", methods=["GET"])
@jwt_required()
def search_id():
    """Binary search for expense by ID.
    
    REQUIRES: Must sort by ID first (O(n log n) one-time cost)
    Then binary search is O(log n) - 50,000× faster than linear for 1M items!
    
    Query parameters:
    - expense_id: Expense ID to search for
    
    Time Complexity: O(n log n) sort + O(log n) search
    """
    expense_id = request.args.get("expense_id")
    if not expense_id:
        return error_response("Missing 'expense_id' query parameter", 400)
    
    try:
        expense_id = int(expense_id)
    except ValueError:
        return error_response("expense_id must be an integer", 400)
    
    return search_by_id(int(get_jwt_identity()), expense_id)


@expense_bp.route("/search/date", methods=["GET"])
@jwt_required()
def search_date():
    """Binary search for expenses on a specific date.
    
    REQUIRES: Must sort by date first
    
    Query parameters:
    - date: Date to search for (format: YYYY-MM-DD)
    
    Time Complexity: O(n log n) sort + O(log n + k) search
    where k = number of expenses on that date
    """
    date_str = request.args.get("date")
    if not date_str:
        return error_response("Missing 'date' query parameter", 400)
    
    return search_by_date(int(get_jwt_identity()), date_str)


@expense_bp.route("/search/date-range", methods=["GET"])
@jwt_required()
def search_date_range():
    """Binary search for expenses within a date range.
    
    REQUIRES: Must sort by date first
    
    Query parameters:
    - start_date: Start date (format: YYYY-MM-DD)
    - end_date: End date (format: YYYY-MM-DD)
    
    Time Complexity: O(n log n) sort + O(log n + k) search
    where k = number of expenses in range
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    if not start_date or not end_date:
        return error_response(
            "Missing 'start_date' or 'end_date' query parameters", 400
        )
    
    return search_by_date_range(int(get_jwt_identity()), start_date, end_date)
