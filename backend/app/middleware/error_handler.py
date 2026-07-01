"""
Global error handlers — converts exceptions to consistent JSON responses.
Registered in the app factory via register_error_handlers(app).
"""

from flask import jsonify
from marshmallow import ValidationError


def register_error_handlers(app):
    """Attach error handlers to the Flask app."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message": "Bad request",
            "errors": str(error),
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "message": "Unauthorized — valid authentication required",
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "message": "Forbidden — you do not have access to this resource",
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Resource not found",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "message": "Method not allowed",
        }), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            "success": False,
            "message": "Conflict — resource already exists",
        }), 409

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "message": "Unprocessable entity",
            "errors": str(error),
        }), 422

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(error):
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": error.messages,
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "message": "Internal server error",
        }), 500
