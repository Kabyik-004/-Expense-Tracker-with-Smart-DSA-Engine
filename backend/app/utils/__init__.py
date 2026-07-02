"""
Utilities package.
Shared helper functions used across the application.
"""


def get_value_by_key(item, key):
    """Extract a value from an item by attribute name, dict key, or callable."""
    if callable(key):
        return key(item)
    elif isinstance(item, dict):
        return item.get(key)
    elif hasattr(item, key):
        return getattr(item, key)
    else:
        return item
