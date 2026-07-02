"""
Expense controller — CRUD operations, filtering, and in-memory summaries for expenses.
"""

import json
import time
from datetime import datetime

from app import db
from app.models.expense import Expense
from app.models.undo_history import UndoHistory
from app.schemas.expense_schema import (
    CreateExpenseSchema,
    UpdateExpenseSchema,
    ExpenseResponseSchema,
)
from app.utils.responses import success_response, error_response
from app.controllers.activity_controller import log_activity
from app.services.hash_table import HashTable
from app.services.stack import Stack
from app.services.search import (
    search_expenses_by_title,
    search_expenses_by_description,
    search_expenses_by_category,
    search_expense_by_id,
    search_expenses_by_date,
    search_expenses_by_date_range,
)
from app.services.merge_sort import merge_sort

create_expense_schema = CreateExpenseSchema()
update_expense_schema = UpdateExpenseSchema()
expense_response_schema = ExpenseResponseSchema()

class _TTLCache:
    """Simple TTL cache that expires entries after timeout_seconds."""

    def __init__(self, timeout_seconds=300):
        self._store = {}
        self._timeout = timeout_seconds

    def get(self, key):
        entry = self._store.get(key)
        if entry is None:
            return None
        value, timestamp = entry
        if time.time() - timestamp > self._timeout:
            del self._store[key]
            return None
        return value

    def set(self, key, value):
        self._store[key] = (value, time.time())

    def delete(self, key):
        self._store.pop(key, None)

    def contains(self, key):
        return self.get(key) is not None

    def clear(self):
        self._store.clear()


_user_summaries = _TTLCache()
_undo_stacks = _TTLCache()


def reset_expense_summaries():
    _user_summaries.clear()
    _undo_stacks.clear()


def _month_key(date_value):
    return date_value.strftime("%Y-%m")


def _apply_expense_to_tables(tables, expense, add=True):
    category_key = expense.category_id or "uncategorized"
    month_key = _month_key(expense.date)

    if add:
        tables["category_totals"].add(category_key, expense.amount)
        tables["category_counts"].add(category_key, 1)
        tables["monthly_totals"].add(month_key, expense.amount)
    else:
        tables["category_totals"].remove(category_key, expense.amount)
        tables["category_counts"].remove(category_key, 1)
        tables["monthly_totals"].remove(month_key, expense.amount)


def _build_user_summaries_from_db(user_id):
    tables = {
        "category_totals": HashTable(),
        "category_counts": HashTable(),
        "monthly_totals": HashTable(),
    }
    expenses = Expense.query.filter_by(user_id=user_id).all()
    for expense in expenses:
        _apply_expense_to_tables(tables, expense, add=True)
    return tables


def _get_user_summary_tables(user_id):
    tables = _user_summaries.get(user_id)
    if tables is None:
        tables = _build_user_summaries_from_db(user_id)
        _user_summaries.set(user_id, tables)
    return tables


def _apply_expense_to_summaries(user_id, expense, add=True):
    tables = _user_summaries.get(user_id)
    if tables is None:
        _user_summaries.set(user_id, _build_user_summaries_from_db(user_id))
        return
    _apply_expense_to_tables(tables, expense, add=add)


def create_expense(user_id, data):
    data = create_expense_schema.load(data)
    expense = Expense(
        user_id=user_id,
        title=data["title"],
        amount=data["amount"],
        description=data.get("description"),
        date=data.get("date"),
        category_id=data.get("category_id"),
        payment_method=data.get("payment_method", "cash"),
        is_recurring=data.get("is_recurring", False),
        notes=data.get("notes"),
    )

    db.session.add(expense)
    db.session.commit()

    _apply_expense_to_summaries(user_id, expense, add=True)

    _track_undo_create(user_id, expense)

    log_activity(user_id, "create", "expense", expense.id, f"Created expense: {expense.title}")

    return success_response(
        data={"expense": expense_response_schema.dump(expense)},
        message="Expense created successfully",
        status_code=201,
    )


def list_expenses(user_id):
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    return success_response(
        data={"expenses": expense_response_schema.dump(expenses, many=True)},
        message="Expenses retrieved successfully",
    )


def get_expense(user_id, expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return error_response("Expense not found", 404)
    return success_response(
        data={"expense": expense_response_schema.dump(expense)},
        message="Expense retrieved successfully",
    )


def update_expense(user_id, expense_id, data):
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return error_response("Expense not found", 404)

    old_category_id = expense.category_id or "uncategorized"
    old_amount = expense.amount
    old_month = _month_key(expense.date)

    # Save the old state for undo tracking BEFORE updating
    old_expense_snapshot = Expense(
        id=expense.id,
        user_id=expense.user_id,
        title=expense.title,
        amount=expense.amount,
        description=expense.description,
        date=expense.date,
        category_id=expense.category_id,
        payment_method=expense.payment_method,
        is_recurring=expense.is_recurring,
        notes=expense.notes,
    )

    data = update_expense_schema.load(data)

    if "title" in data:
        expense.title = data["title"]
    if "amount" in data:
        expense.amount = data["amount"]
    if "description" in data:
        expense.description = data["description"]
    if "date" in data:
        expense.date = data["date"]
    if "category_id" in data:
        expense.category_id = data["category_id"]
    if "payment_method" in data:
        expense.payment_method = data["payment_method"]
    if "is_recurring" in data:
        expense.is_recurring = data["is_recurring"]
    if "notes" in data:
        expense.notes = data["notes"]

    db.session.commit()

    tables = _user_summaries.get(user_id)
    if tables is not None:
        old_expense = Expense(
            user_id=user_id,
            title=expense.title,
            amount=old_amount,
            date=datetime.strptime(old_month + "-01", "%Y-%m-%d").date(),
            category_id=old_category_id,
        )
        _apply_expense_to_tables(tables, old_expense, add=False)
        _apply_expense_to_tables(tables, expense, add=True)
    else:
        _user_summaries.set(user_id, _build_user_summaries_from_db(user_id))

    _track_undo_update(user_id, old_expense_snapshot)

    log_activity(user_id, "update", "expense", expense.id, f"Updated expense: {expense.title}")

    return success_response(
        data={"expense": expense_response_schema.dump(expense)},
        message="Expense updated successfully",
    )


def delete_expense(user_id, expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return error_response("Expense not found", 404)

    # Track undo operation BEFORE deleting
    _track_undo_delete(user_id, expense)
    
    _apply_expense_to_summaries(user_id, expense, add=False)
    db.session.delete(expense)
    db.session.commit()

    log_activity(user_id, "delete", "expense", expense.id, f"Deleted expense: {expense.title}")

    return success_response(message="Expense deleted successfully")


def sort_expenses_by_field(user_id, sort_by="amount", ascending=True):
    """Sort expenses using merge sort algorithm.
    
    Supported fields: amount, date, category_id, title
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    from app.services.merge_sort import sort_expenses
    
    expenses = Expense.query.filter_by(user_id=user_id).all()
    
    if not expenses:
        return success_response(
            data={"expenses": []},
            message="No expenses found",
        )
    
    # Validate sort_by field
    valid_fields = ["amount", "date", "category_id", "title"]
    if sort_by not in valid_fields:
        return error_response(
            f"Invalid sort field. Must be one of: {', '.join(valid_fields)}",
            400,
        )
    
    sorted_expenses = sort_expenses(expenses, sort_by=sort_by, ascending=ascending)
    
    return success_response(
        data={"expenses": expense_response_schema.dump(sorted_expenses, many=True)},
        message=f"Expenses sorted by {sort_by} ({('ascending' if ascending else 'descending')})",
    )


def sort_expenses_multi_field(user_id, sort_config):
    """Sort expenses by multiple fields using stable merge sort.
    
    sort_config format:
    {
        "sort_fields": ["category_id", "amount"],
        "ascending": [true, false]
    }
    
    Sorts by amount descending, then category ascending (for tiebreaks).
    Time Complexity: O(k * n log n) where k = number of sort fields
    """
    from app.services.merge_sort import sort_expenses_multi
    
    expenses = Expense.query.filter_by(user_id=user_id).all()
    
    if not expenses:
        return success_response(
            data={"expenses": []},
            message="No expenses found",
        )
    
    sort_fields = sort_config.get("sort_fields", [])
    ascending_list = sort_config.get("ascending", [True] * len(sort_fields))
    
    if not sort_fields:
        return error_response("sort_fields is required", 400)
    
    # Validate sort fields
    valid_fields = ["amount", "date", "category_id", "title"]
    for field in sort_fields:
        if field not in valid_fields:
            return error_response(
                f"Invalid sort field: {field}. Must be one of: {', '.join(valid_fields)}",
                400,
            )
    
    sorted_expenses = sort_expenses_multi(
        expenses,
        sort_fields=sort_fields,
        ascending_list=ascending_list,
    )
    
    return success_response(
        data={"expenses": expense_response_schema.dump(sorted_expenses, many=True)},
        message=f"Expenses sorted by {', '.join(sort_fields)}",
    )


def get_category_totals(user_id):
    tables = _get_user_summary_tables(user_id)
    return success_response(
        data={"category_totals": tables["category_totals"].to_dict()},
        message="Category totals retrieved successfully",
    )


def get_category_counts(user_id):
    tables = _get_user_summary_tables(user_id)
    return success_response(
        data={"category_counts": tables["category_counts"].to_dict()},
        message="Category counts retrieved successfully",
    )


def get_monthly_totals(user_id):
    tables = _get_user_summary_tables(user_id)
    return success_response(
        data={"monthly_totals": tables["monthly_totals"].to_dict()},
        message="Monthly totals retrieved successfully",
    )


# ── UNDO/REDO STACK (Max 10 operations per user) ──────────────────────────


def _undo_op_from_history(record):
    return {
        "action": record.action,
        "entity_type": record.entity_type,
        "entity_id": record.entity_id,
        "snapshot": record.snapshot,
    }


def _hydrate_undo_stack_from_db(user_id, max_size=10):
    stack = Stack(max_size=max_size)
    history = (
        UndoHistory.query.filter_by(user_id=user_id, entity_type="expense")
        .order_by(UndoHistory.id.asc())
        .all()
    )
    recent = history[-max_size:] if len(history) > max_size else history
    for record in recent:
        stack.push(_undo_op_from_history(record))
    return stack


def _get_user_undo_stack(user_id, max_size=10):
    stack = _undo_stacks.get(user_id)
    if stack is None:
        stack = _hydrate_undo_stack_from_db(user_id, max_size)
        _undo_stacks.set(user_id, stack)
    return stack


def _remove_latest_undo_history(user_id):
    latest = (
        UndoHistory.query.filter_by(user_id=user_id, entity_type="expense")
        .order_by(UndoHistory.id.desc())
        .first()
    )
    if latest:
        db.session.delete(latest)
        db.session.commit()


def _serialize_expense(expense):
    """Convert Expense object to JSON-serializable dict for undo snapshot."""
    return {
        "id": expense.id,
        "user_id": expense.user_id,
        "title": expense.title,
        "amount": expense.amount,
        "description": expense.description,
        "date": expense.date.isoformat() if expense.date else None,
        "category_id": expense.category_id,
        "payment_method": expense.payment_method,
        "is_recurring": expense.is_recurring,
        "notes": expense.notes,
    }


def _track_undo_create(user_id, expense):
    """Track undo for expense creation."""
    undo_stack = _get_user_undo_stack(user_id)
    undo_op = {
        "action": "CREATE",
        "entity_type": "expense",
        "entity_id": expense.id,
        "snapshot": None,  # No snapshot for create (nothing existed before)
    }
    undo_stack.push(undo_op)
    
    # Also persist to database
    undo_history = UndoHistory(
        user_id=user_id,
        action="CREATE",
        entity_type="expense",
        entity_id=expense.id,
        snapshot=None,
    )
    db.session.add(undo_history)
    db.session.commit()


def _track_undo_update(user_id, old_expense):
    """Track undo for expense update (store snapshot of old state)."""
    undo_stack = _get_user_undo_stack(user_id)
    undo_op = {
        "action": "UPDATE",
        "entity_type": "expense",
        "entity_id": old_expense.id,
        "snapshot": json.dumps(_serialize_expense(old_expense)),
    }
    undo_stack.push(undo_op)
    
    # Also persist to database
    undo_history = UndoHistory(
        user_id=user_id,
        action="UPDATE",
        entity_type="expense",
        entity_id=old_expense.id,
        snapshot=json.dumps(_serialize_expense(old_expense)),
    )
    db.session.add(undo_history)
    db.session.commit()


def _track_undo_delete(user_id, expense):
    """Track undo for expense deletion (store snapshot of deleted expense)."""
    undo_stack = _get_user_undo_stack(user_id)
    undo_op = {
        "action": "DELETE",
        "entity_type": "expense",
        "entity_id": expense.id,
        "snapshot": json.dumps(_serialize_expense(expense)),
    }
    undo_stack.push(undo_op)
    
    # Also persist to database
    undo_history = UndoHistory(
        user_id=user_id,
        action="DELETE",
        entity_type="expense",
        entity_id=expense.id,
        snapshot=json.dumps(_serialize_expense(expense)),
    )
    db.session.add(undo_history)
    db.session.commit()


def undo_last_operation(user_id):
    """
    Undo the last expense operation (create, update, or delete).
    
    Time Complexity: O(1) for stack pop + O(1) for database operation
    """
    undo_stack = _get_user_undo_stack(user_id)
    
    if undo_stack.is_empty():
        return error_response("No undo history available", 400)
    
    undo_op = undo_stack.pop()
    
    try:
        if undo_op["action"] == "CREATE":
            # Undo create by deleting the expense
            expense = Expense.query.filter_by(
                id=undo_op["entity_id"],
                user_id=user_id
            ).first()
            if expense:
                tables = _user_summaries.get(user_id)
                if tables is not None:
                    _apply_expense_to_tables(tables, expense, add=False)
                else:
                    _user_summaries.set(user_id, _build_user_summaries_from_db(user_id))
                db.session.delete(expense)
                db.session.commit()
                _remove_latest_undo_history(user_id)
                return success_response(
                    data={"expense_id": undo_op["entity_id"]},
                    message=f"Undo: Deleted expense {undo_op['entity_id']}",
                )
        
        elif undo_op["action"] == "UPDATE":
            # Undo update by restoring old values
            old_data = json.loads(undo_op["snapshot"])
            expense = Expense.query.filter_by(
                id=undo_op["entity_id"],
                user_id=user_id
            ).first()
            if expense:
                tables = _user_summaries.get(user_id)
                if tables is not None:
                    _apply_expense_to_tables(tables, expense, add=False)

                expense.title = old_data["title"]
                expense.amount = old_data["amount"]
                expense.description = old_data["description"]
                expense.date = datetime.fromisoformat(old_data["date"]).date() if old_data["date"] else None
                expense.category_id = old_data["category_id"]
                expense.payment_method = old_data["payment_method"]
                expense.is_recurring = old_data["is_recurring"]
                expense.notes = old_data["notes"]
                
                db.session.commit()

                tables = _user_summaries.get(user_id)
                if tables is not None:
                    _apply_expense_to_tables(tables, expense, add=True)
                else:
                    _user_summaries.set(user_id, _build_user_summaries_from_db(user_id))
                _remove_latest_undo_history(user_id)

                return success_response(
                    data={"expense": expense_response_schema.dump(expense)},
                    message=f"Undo: Restored expense {undo_op['entity_id']} to previous state",
                )
        
        elif undo_op["action"] == "DELETE":
            # Undo delete by restoring the expense
            old_data = json.loads(undo_op["snapshot"])
            
            # Recreate the expense with original data
            expense = Expense(
                id=old_data["id"],
                user_id=user_id,
                title=old_data["title"],
                amount=old_data["amount"],
                description=old_data["description"],
                date=datetime.fromisoformat(old_data["date"]).date() if old_data["date"] else None,
                category_id=old_data["category_id"],
                payment_method=old_data["payment_method"],
                is_recurring=old_data["is_recurring"],
                notes=old_data["notes"],
            )
            
            db.session.add(expense)
            db.session.commit()

            _apply_expense_to_summaries(user_id, expense, add=True)
            _remove_latest_undo_history(user_id)

            return success_response(
                data={"expense": expense_response_schema.dump(expense)},
                message=f"Undo: Restored deleted expense {undo_op['entity_id']}",
            )
        
        return error_response("Unknown undo operation", 400)
    
    except Exception as e:
        return error_response(f"Undo failed: {str(e)}", 500)


def get_undo_stack_status(user_id):
    """Get current undo stack status (size and top operation)."""
    undo_stack = _get_user_undo_stack(user_id)
    top_op = undo_stack.peek()
    
    return success_response(
        data={
            "stack_size": undo_stack.size(),
            "max_size": undo_stack._max_size,
            "is_empty": undo_stack.is_empty(),
            "top_operation": top_op,
        },
        message="Undo stack status retrieved",
    )


def clear_undo_stack(user_id):
    """Clear all undo history for a user."""
    stack = _undo_stacks.get(user_id)
    if stack is not None:
        stack.clear()

    UndoHistory.query.filter_by(user_id=user_id, entity_type="expense").delete()
    db.session.commit()

    return success_response(
        message="Undo stack cleared",
    )


# ============================================================================
# SEARCH OPERATIONS - Linear and Binary Search
# ============================================================================


def search_by_title(user_id, query):
    """
    Linear search for expenses by title.
    
    Time Complexity: O(n) - checks all expenses
    
    Args:
        user_id: User ID
        query (str): Search term (case-insensitive substring match)
    
    Returns:
        dict: success_response with list of matching expenses
    """
    expenses = Expense.query.filter_by(user_id=user_id).all()
    results = search_expenses_by_title(expenses, query)
    
    serialized = [_serialize_expense(exp) for exp in results]
    
    return success_response(
        data=serialized,
        message=f"Found {len(results)} expenses matching '{query}'",
    )


def search_by_description(user_id, query):
    """
    Linear search for expenses by description.
    
    Time Complexity: O(n)
    
    Args:
        user_id: User ID
        query (str): Search term (case-insensitive substring match)
    
    Returns:
        dict: success_response with list of matching expenses
    """
    expenses = Expense.query.filter_by(user_id=user_id).all()
    results = search_expenses_by_description(expenses, query)
    
    serialized = [_serialize_expense(exp) for exp in results]
    
    return success_response(
        data=serialized,
        message=f"Found {len(results)} expenses matching '{query}'",
    )


def search_by_category(user_id, category_id):
    """
    Linear search for expenses by category ID.
    
    Time Complexity: O(n)
    
    Args:
        user_id: User ID
        category_id: Category ID to search for
    
    Returns:
        dict: success_response with list of matching expenses
    """
    expenses = Expense.query.filter_by(user_id=user_id).all()
    results = search_expenses_by_category(expenses, category_id)
    
    serialized = [_serialize_expense(exp) for exp in results]
    
    return success_response(
        data=serialized,
        message=f"Found {len(results)} expenses in category {category_id}",
    )


def search_by_id(user_id, expense_id):
    """
    Binary search for expense by ID.
    
    REQUIRES: Must sort by ID first (O(n log n) one-time cost)
    Then binary search is O(log n) - extremely fast!
    
    Time Complexity: O(n log n) sort + O(log n) search
    
    Args:
        user_id: User ID
        expense_id: Expense ID to find
    
    Returns:
        dict: success_response with expense if found
    """
    # Get all expenses for user
    expenses = Expense.query.filter_by(user_id=user_id).all()
    
    if not expenses:
        return error_response("No expenses found", 404)
    
    # Sort by ID (O(n log n))
    sorted_expenses = merge_sort(expenses, key="id", ascending=True)
    
    # Binary search (O(log n))
    expense = search_expense_by_id(sorted_expenses, expense_id)
    
    if expense is None:
        return error_response(f"Expense {expense_id} not found", 404)
    
    serialized = _serialize_expense(expense)
    
    return success_response(
        data=serialized,
        message=f"Found expense {expense_id}",
    )


def search_by_date(user_id, target_date):
    """
    Binary search for expenses on a specific date.
    
    REQUIRES: Must sort by date first
    
    Time Complexity: O(n log n) sort + O(log n + k) search
    where k = number of expenses on that date
    
    Args:
        user_id: User ID
        target_date: Date to search for (datetime.date or string "YYYY-MM-DD")
    
    Returns:
        dict: success_response with list of expenses on that date
    """
    from datetime import datetime as dt
    
    # Parse date string if needed
    if isinstance(target_date, str):
        target_date = dt.strptime(target_date, "%Y-%m-%d").date()
    
    # Get all expenses for user
    expenses = Expense.query.filter_by(user_id=user_id).all()
    
    if not expenses:
        return success_response(
            data=[],
            message="No expenses found",
        )
    
    # Sort by date (O(n log n))
    sorted_expenses = merge_sort(expenses, key="date", ascending=True)
    
    # Binary search for all expenses on that date (O(log n + k))
    results = search_expenses_by_date(sorted_expenses, target_date)
    
    serialized = [_serialize_expense(exp) for exp in results]
    
    return success_response(
        data=serialized,
        message=f"Found {len(results)} expenses on {target_date}",
    )


def search_by_date_range(user_id, start_date, end_date):
    """
    Binary search for expenses within a date range [start_date, end_date].
    
    REQUIRES: Must sort by date first
    
    Time Complexity: O(n log n) sort + O(log n + k) search
    where k = number of expenses in range
    
    Args:
        user_id: User ID
        start_date: Start date (datetime.date or string "YYYY-MM-DD")
        end_date: End date (datetime.date or string "YYYY-MM-DD")
    
    Returns:
        dict: success_response with list of expenses in range
    """
    from datetime import datetime as dt
    
    # Parse date strings if needed
    if isinstance(start_date, str):
        start_date = dt.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = dt.strptime(end_date, "%Y-%m-%d").date()
    
    # Validate range
    if start_date > end_date:
        return error_response("start_date must be <= end_date", 400)
    
    # Get all expenses for user
    expenses = Expense.query.filter_by(user_id=user_id).all()
    
    if not expenses:
        return success_response(
            data=[],
            message="No expenses found",
        )
    
    # Sort by date (O(n log n))
    sorted_expenses = merge_sort(expenses, key="date", ascending=True)
    
    # Binary search for all expenses in range (O(log n + k))
    results = search_expenses_by_date_range(
        sorted_expenses, start_date, end_date
    )
    
    serialized = [_serialize_expense(exp) for exp in results]
    
    return success_response(
        data=serialized,
        message=f"Found {len(results)} expenses between {start_date} and {end_date}",
    )
