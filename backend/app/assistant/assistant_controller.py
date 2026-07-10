import json
import logging

from flask import stream_with_context, Response
from flask_jwt_extended import get_jwt_identity

from app.assistant.assistant_service import process_message_stream
from app.assistant.classifier import classify_message
from app.assistant.extractor import extract_entities
from app.assistant.conversation_memory import clear_session, get_session
from app.utils.responses import error_response, success_response

logger = logging.getLogger(__name__)


def handle_chat(request_data):
    if not request_data or "message" not in request_data:
        return error_response("Message is required", 400)

    message = request_data["message"].strip()
    if not message:
        return error_response("Message cannot be empty", 400)

    history = request_data.get("history", None)
    user_id = int(get_jwt_identity())

    logger.debug("Chat from user %s: %.60s", user_id, message)

    def generate():
        for chunk in process_message_stream(message, history, user_id):
            if "error" in chunk:
                yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: {\"done\": true}\n\n"
                return
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: {\"done\": true}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def handle_classify(request_data):
    if not request_data or "message" not in request_data:
        return error_response("Message is required", 400)

    message = request_data["message"].strip()
    if not message:
        return error_response("Message cannot be empty", 400)

    user_id = int(get_jwt_identity())
    result = classify_message(message)
    logger.debug("Classified user %s message as '%s' (%.2f)", user_id, result["intent"], result["confidence"])

    return success_response(data=result)


def handle_extract(request_data):
    if not request_data or "message" not in request_data:
        return error_response("Message is required", 400)

    message = request_data["message"].strip()
    if not message:
        return error_response("Message cannot be empty", 400)

    user_id = int(get_jwt_identity())
    result = extract_entities(message)
    logger.debug("Extracted entities for user %s: %s", user_id, result)

    return success_response(data=result)


def handle_clear_session(request_data):
    user_id = int(get_jwt_identity())
    clear_session(user_id)
    logger.debug("Cleared conversation session for user %s", user_id)
    return success_response(message="Conversation session cleared")


def handle_session_status(request_data):
    user_id = int(get_jwt_identity())
    session = get_session(user_id)
    if session:
        return success_response(data={
            "active": True,
            "intent": session["intent"],
            "missing_fields": session["missing_fields"],
        })
    return success_response(data={"active": False})
