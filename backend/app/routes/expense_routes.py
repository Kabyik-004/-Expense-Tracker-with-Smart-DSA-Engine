"""
Expense routes — /api/expenses/*
Endpoints: CRUD, filter, search.
"""

from flask import Blueprint

expense_bp = Blueprint("expenses", __name__)
