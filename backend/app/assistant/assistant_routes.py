"""
Assistant routes — HTTP endpoints for the AI Assistant.
All routes are registered under the /api/assistant blueprint.

Endpoints:
  POST /api/assistant/chat            → Conversational chat (SSE stream)
  POST /api/assistant/classify        → Intent classification (JSON)
  POST /api/assistant/extract         → Entity extraction (JSON)
  POST /api/assistant/clear           → Clear active conversation session
  GET  /api/assistant/session         → Get active session status
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.assistant.assistant_controller import (
    handle_chat,
    handle_classify,
    handle_extract,
    handle_clear_session,
    handle_session_status,
)

assistant_bp = Blueprint("assistant", __name__)


@assistant_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat_route():
    """
    POST /api/assistant/chat
    Body: { "message": "…", "history": […] }
    """
    return handle_chat(request.get_json())


@assistant_bp.route("/classify", methods=["POST"])
@jwt_required()
def classify_route():
    """
    POST /api/assistant/classify
    Body: { "message": "…" }
    Returns: { "intent": "...", "confidence": 0.95, "entities": {...} }
    """
    return handle_classify(request.get_json())


@assistant_bp.route("/extract", methods=["POST"])
@jwt_required()
def extract_route():
    """
    POST /api/assistant/extract
    Body: { "message": "…" }
    Returns: { "amount": 450, "category": "food", "merchant": "Pizza Hut",
               "payment_method": "upi", "date": "yesterday", "notes": "for dinner" }
    Missing fields are null — never guesses.
    """
    return handle_extract(request.get_json())


@assistant_bp.route("/clear", methods=["POST"])
@jwt_required()
def clear_route():
    """
    POST /api/assistant/clear
    Clears the active conversation session for the current user.
    """
    return handle_clear_session(request.get_json())


@assistant_bp.route("/session", methods=["GET"])
@jwt_required()
def session_route():
    """
    GET /api/assistant/session
    Returns { "active": true/false, "intent": "...", "missing_fields": [...] }
    """
    return handle_session_status(None)
