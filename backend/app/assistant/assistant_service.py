import logging
import os

from flask import current_app

from app.assistant.gemini_provider import stream_chat
from app.assistant.system_prompt import SYSTEM_PROMPT
from app.assistant.classifier import classify_message
from app.assistant.extractor import extract_entities
from app.assistant.slot_filler import (
    REQUIRED_FIELDS,
    get_missing_fields,
    get_next_question,
    extract_from_slot_answer,
)
from app.assistant.conversation_memory import (
    get_session,
    create_session,
    update_session,
    clear_session,
    add_history,
)
from app.assistant.tool_executor import execute_tool, TOOLS_BY_INTENT, get_tool
from app.assistant.knowledge_base import find_answer

logger = logging.getLogger(__name__)


def _get_api_key():
    try:
        return current_app.config.get("GEMINI_API_KEY", "")
    except RuntimeError:
        return os.getenv("GEMINI_API_KEY", "")


def _get_system_prompt():
    env_prompt = os.getenv("SYSTEM_PROMPT")
    if env_prompt and env_prompt.strip():
        return env_prompt.strip()
    return SYSTEM_PROMPT


def _needs_slot_filling(intent):
    return intent in REQUIRED_FIELDS and REQUIRED_FIELDS[intent]


def process_message_stream(message, history=None, user_id=None):
    api_key = _get_api_key()
    system_prompt = _get_system_prompt()
    session = get_session(user_id) if user_id else None

    if session:
        yield from _handle_slot_fill(message, session, user_id, api_key, system_prompt)
    else:
        yield from _handle_new_message(message, history, user_id, api_key, system_prompt)


def _handle_new_message(message, history, user_id, api_key, system_prompt):
    knowledge_answer = find_answer(message)
    if knowledge_answer:
        for chunk in _yield_text(knowledge_answer):
            yield chunk
        return

    result = classify_message(message)
    intent = result["intent"]
    entities = result.get("entities", {})

    merged_entities = dict(entities)
    new_entities = extract_entities(message)
    for k, v in new_entities.items():
        if v is not None:
            merged_entities[k] = v

    needs_slotting = _needs_slot_filling(intent)

    if needs_slotting:
        missing = get_missing_fields(intent, merged_entities)
        if missing:
            session = create_session(user_id, intent, merged_entities, missing)
            question = get_next_question(missing, 0)
            add_history(user_id, "user", message)
            add_history(user_id, "assistant", question)
            for chunk in _yield_text(question):
                yield chunk
            return

    if intent in ("unknown", "general_help", "navigation_help", "bank_statement_query"):
        if api_key:
            for chunk in stream_chat(api_key, system_prompt, message, history):
                yield chunk
        else:
            tool_result = execute_tool(user_id, intent, merged_entities)
            for chunk in _yield_text(tool_result.get("reply", "")):
                yield chunk
        return

    tool_result = execute_tool(user_id, intent, merged_entities, message)
    for chunk in _yield_text(tool_result.get("reply", "")):
        yield chunk


def _handle_slot_fill(message, session, user_id, api_key, system_prompt):
    intent = session["intent"]
    missing = session["missing_fields"]
    prev_entities = dict(session["entities"])

    if not missing:
        clear_session(user_id)
        for chunk in _handle_new_message(message, None, user_id, api_key, system_prompt):
            yield chunk
        return

    target_field = missing[0]
    new_entities = extract_from_slot_answer(message, target_field)
    session = update_session(user_id, new_entities)

    if session is None:
        clear_session(user_id)
        for chunk in _handle_new_message(message, None, user_id, api_key, system_prompt):
            yield chunk
        return

    any_filled = any(
        session["entities"].get(k) is not None and prev_entities.get(k) is None
        for k in session["entities"]
    )

    if not any_filled:
        question = f"Please tell me the {target_field.replace('_', ' ')}."
        add_history(user_id, "user", message)
        add_history(user_id, "assistant", question)
        for chunk in _yield_text(question):
            yield chunk
        return

    remaining = get_missing_fields(intent, session["entities"])

    if remaining:
        session["missing_fields"] = remaining
        question = get_next_question(remaining, 0)
        add_history(user_id, "user", message)
        add_history(user_id, "assistant", question)
        for chunk in _yield_text(question):
            yield chunk
    else:
        add_history(user_id, "user", message)
        clear_session(user_id)

        tool_result = execute_tool(user_id, intent, session["entities"], message)
        reply = tool_result.get("reply", "")
        for chunk in _yield_text(reply):
            yield chunk


def _yield_text(text):
    words = text.split(" ")
    for i, word in enumerate(words):
        prefix = " " if i > 0 else ""
        yield {"reply": prefix + word}
