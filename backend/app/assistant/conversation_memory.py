import logging
import time

logger = logging.getLogger(__name__)

_SESSIONS = {}

SESSION_TTL = 600

def get_session(user_id):
    session = _SESSIONS.get(user_id)
    if session and time.time() - session["updated_at"] > SESSION_TTL:
        logger.debug("Session for user %s expired, removing", user_id)
        del _SESSIONS[user_id]
        return None
    if session:
        session["updated_at"] = time.time()
    return session

def create_session(user_id, intent, entities, missing_fields):
    session = {
        "intent": intent,
        "entities": dict(entities),
        "missing_fields": list(missing_fields),
        "current_field_index": 0,
        "history": [],
        "updated_at": time.time(),
        "created_at": time.time(),
    }
    _SESSIONS[user_id] = session
    logger.debug("Created session for user %s: intent=%s, fields=%s", user_id, intent, missing_fields)
    return session

def update_session(user_id, entities, missing_fields=None, intent=None):
    session = get_session(user_id)
    if not session:
        return None
    for k, v in entities.items():
        if v is not None:
            session["entities"][k] = v
    if missing_fields is not None:
        session["missing_fields"] = list(missing_fields)
        session["current_field_index"] = 0
    if intent is not None:
        session["intent"] = intent
    session["updated_at"] = time.time()
    return session

def clear_session(user_id):
    _SESSIONS.pop(user_id, None)

def add_history(user_id, role, text):
    session = get_session(user_id)
    if session:
        session["history"].append({"role": role, "text": text})
        session["updated_at"] = time.time()

def cleanup_expired():
    now = time.time()
    expired = [uid for uid, s in _SESSIONS.items() if now - s["updated_at"] > SESSION_TTL]
    for uid in expired:
        del _SESSIONS[uid]
    if expired:
        logger.debug("Cleaned %d expired sessions", len(expired))
