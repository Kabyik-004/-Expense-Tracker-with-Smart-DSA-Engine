"""
Database utilities
Helper functions for initializing, seeding, and resetting the database.
"""

from app import db
from app.models import User, Category  # noqa: F401 — ensures discovery


def init_db(app):
    """Create all tables. Called automatically by the app factory."""
    with app.app_context():
        db.create_all()


def drop_db(app):
    """Drop all tables. Use only in development/testing."""
    with app.app_context():
        db.drop_all()


def reset_db(app):
    """Drop and recreate all tables. USE WITH CAUTION."""
    drop_db(app)
    init_db(app)


def seed_default_categories(app):
    """
    Insert default expense categories for a given user.
    Call after user registration to provide starter categories.
    """
    DEFAULT_CATEGORIES = [
        {"name": "Food & Dining",    "icon": "🍔", "color": "#ef4444"},
        {"name": "Transportation",   "icon": "🚗", "color": "#f97316"},
        {"name": "Shopping",         "icon": "🛍️", "color": "#eab308"},
        {"name": "Entertainment",    "icon": "🎬", "color": "#22c55e"},
        {"name": "Bills & Utilities", "icon": "💡", "color": "#3b82f6"},
        {"name": "Health",           "icon": "🏥", "color": "#06b6d4"},
        {"name": "Education",        "icon": "📚", "color": "#8b5cf6"},
        {"name": "Rent",             "icon": "🏠", "color": "#ec4899"},
        {"name": "Groceries",        "icon": "🛒", "color": "#14b8a6"},
        {"name": "Other",            "icon": "📦", "color": "#6b7280"},
    ]
    return DEFAULT_CATEGORIES


def create_default_categories_for_user(user_id):
    """
    Inserts default categories into the database for a newly registered user.
    Returns the list of created Category objects.
    """
    defaults = seed_default_categories(None)
    categories = []
    for cat in defaults:
        category = Category(
            user_id=user_id,
            name=cat["name"],
            icon=cat["icon"],
            color=cat["color"],
            is_default=True,
        )
        db.session.add(category)
        categories.append(category)
    db.session.commit()
    return categories
