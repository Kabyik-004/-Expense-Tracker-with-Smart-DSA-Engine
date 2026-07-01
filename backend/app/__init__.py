"""
Expense Tracker Backend - Application Factory
"""

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from app.config import Config
from app.middleware.error_handler import register_error_handlers

# Initialize extensions (bound to app in create_app)
db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # ── JWT error callbacks (return JSON instead of HTML) ─────────────
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has expired",
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            "success": False,
            "message": "Invalid token",
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({
            "success": False,
            "message": "Authorization token is missing",
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has been revoked",
        }), 401

    # Register middleware and error handlers
    register_error_handlers(app)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.expense_routes import expense_bp
    from app.routes.category_routes import category_bp
    from app.routes.analytics_routes import analytics_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(expense_bp, url_prefix="/api/expenses")
    app.register_blueprint(category_bp, url_prefix="/api/categories")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    # Ensure instance directory exists for SQLite database
    import os
    os.makedirs(app.instance_path, exist_ok=True)

    # Import models so SQLAlchemy registers all tables
    from app.models import User, Expense, Income, Category, UndoHistory  # noqa: F401

    with app.app_context():
        db.create_all()

    return app

