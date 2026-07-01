"""
Reusable response helpers for consistent API responses.
Every endpoint returns JSON in one of these two formats.
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """
    Standard success response.

    Returns:
        {
            "success": true,
            "message": "...",
            "data": { ... }
        }
    """
    payload = {
        "success": True,
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """
    Standard error response.

    Returns:
        {
            "success": false,
            "message": "...",
            "errors": { ... }   ← optional field-level errors
        }
    """
    payload = {
        "success": False,
        "message": message,
    }
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status_code
