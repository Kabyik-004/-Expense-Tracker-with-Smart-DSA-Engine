import logging

logger = logging.getLogger(__name__)

TOOLS = {
    "add_expense": {
        "name": "add_expense",
        "description": "Create a new expense record",
        "controller": "expense_controller.create_expense",
        "http_method": "POST",
        "http_path": "/api/expenses/",
        "param_mapping": {
            "amount": "amount",
            "title": "title",
            "category": "category_id",
            "payment_method": "payment_method",
            "date": "date",
            "notes": "notes",
            "merchant": "title",
        },
        "required_params": ["amount", "title"],
        "optional_params": ["description", "date", "category_id", "payment_method", "notes", "is_recurring"],
        "success_message": "Expense created successfully",
    },
    "add_income": {
        "name": "add_income",
        "description": "Create a new income record",
        "controller": "income_controller.create_income",
        "http_method": "POST",
        "http_path": "/api/incomes/",
        "param_mapping": {
            "source": "source",
            "amount": "amount",
            "category": "source",
            "date": "date",
            "notes": "notes",
        },
        "required_params": ["amount", "source"],
        "optional_params": ["description", "date", "notes", "is_recurring"],
        "success_message": "Income created successfully",
    },
    "delete_expense": {
        "name": "delete_expense",
        "description": "Delete an existing expense",
        "controller": "expense_controller.delete_expense",
        "http_method": "DELETE",
        "http_path": "/api/expenses/{expense_id}",
        "param_mapping": {
            "expense_id": "expense_id",
        },
        "required_params": ["expense_id"],
        "optional_params": [],
        "success_message": "Expense deleted successfully",
    },
    "update_expense": {
        "name": "update_expense",
        "description": "Update an existing expense",
        "controller": "expense_controller.update_expense",
        "http_method": "PUT",
        "http_path": "/api/expenses/{expense_id}",
        "param_mapping": {
            "expense_id": "expense_id",
            "amount": "amount",
            "title": "title",
            "category": "category_id",
            "payment_method": "payment_method",
            "date": "date",
            "notes": "notes",
        },
        "required_params": ["expense_id"],
        "optional_params": ["title", "amount", "description", "date", "category_id", "payment_method", "notes"],
        "success_message": "Expense updated successfully",
    },
    "search_expense": {
        "name": "search_expense",
        "description": "Search for expenses",
        "controller": "expense_controller.search_by_title",
        "http_method": "GET",
        "http_path": "/api/expenses/search/title",
        "param_mapping": {
            "search_query": "q",
        },
        "required_params": [],
        "optional_params": ["q"],
        "success_message": "Search completed",
    },
    "dashboard_query": {
        "name": "dashboard_query",
        "description": "Get full analytics dashboard",
        "controller": "analytics_controller.dashboard_analytics",
        "http_method": "GET",
        "http_path": "/api/analytics/dashboard",
        "param_mapping": {},
        "required_params": [],
        "optional_params": [],
        "success_message": "Dashboard loaded",
    },
    "analytics_query": {
        "name": "analytics_query",
        "description": "Get analytics overview",
        "controller": "analytics_controller.analytics_overview",
        "http_method": "GET",
        "http_path": "/api/analytics/overview",
        "param_mapping": {},
        "required_params": [],
        "optional_params": [],
        "success_message": "Analytics loaded",
    },
    "calendar_query": {
        "name": "calendar_query",
        "description": "Get time-series data for date queries",
        "controller": "analytics_controller.time_series_analytics",
        "http_method": "GET",
        "http_path": "/api/analytics/time-series",
        "param_mapping": {},
        "required_params": [],
        "optional_params": [],
        "success_message": "Calendar data loaded",
    },
}

TOOLS_BY_INTENT = {
    "add_expense": "add_expense",
    "add_income": "add_income",
    "delete_expense": "delete_expense",
    "update_expense": "update_expense",
    "search_expense": "search_expense",
    "dashboard_query": "dashboard_query",
    "analytics_query": "analytics_query",
    "calendar_query": "calendar_query",
}


def get_tool(intent):
    tool_key = TOOLS_BY_INTENT.get(intent)
    if not tool_key:
        return None
    return TOOLS.get(tool_key)
