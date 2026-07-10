import json
import logging
import time
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL = "gemini-2.0-flash"
MAX_RETRIES = 3
INITIAL_BACKOFF = 2.0


def _build_contents(message, history):
    contents = []
    for entry in history or []:
        role = entry.get("role", "user")
        text = entry.get("text", "")
        if text:
            gemini_role = "model" if role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": text}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    return contents


def _attempt_stream(api_key, payload):
    url = f"{BASE_URL}/{MODEL}:streamGenerateContent?alt=sse&key={api_key}"
    resp = requests.post(url, json=payload, stream=True, timeout=60)
    resp.raise_for_status()

    for line in resp.iter_lines():
        if not line:
            continue
        decoded = line.decode("utf-8")
        if not decoded.startswith("data: "):
            continue
        data_str = decoded[6:]
        if data_str == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
            candidates = chunk.get("candidates", [])
            if not candidates:
                continue
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                text = part.get("text", "")
                if text:
                    yield {"reply": text}
        except json.JSONDecodeError:
            continue


def stream_chat(api_key, system_prompt, message, history=None):
    if not api_key:
        logger.error("GEMINI_API_KEY not configured")
        return

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": _build_contents(message, history),
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 8192,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ],
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug("Gemini attempt %d/%d (%s)", attempt, MAX_RETRIES, MODEL)
            yield from _attempt_stream(api_key, payload)
            return
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            body = e.response.text if e.response is not None else ""
            logger.error("Gemini HTTP %d (attempt %d): %s", status, attempt, body)

            if status == 403:
                return
            if status == 429 and attempt < MAX_RETRIES:
                backoff = INITIAL_BACKOFF * (2 ** (attempt - 1))
                logger.warning("Rate limited, retrying in %.1fs (attempt %d/%d)", backoff, attempt, MAX_RETRIES - 1)
                time.sleep(backoff)
                continue

            last_error = status
            break

        except requests.exceptions.ConnectionError:
            logger.error("Gemini connection failed (attempt %d)", attempt)
            last_error = "connection"
            break

        except requests.exceptions.Timeout:
            logger.error("Gemini timeout (attempt %d)", attempt)
            last_error = "timeout"
            break

    if last_error == 403:
        return
    if last_error == "connection":
        return
    if last_error == "timeout":
        return


def chat(api_key, system_prompt, message, history=None):
    full_reply = []
    for chunk in stream_chat(api_key, system_prompt, message, history):
        if "reply" in chunk:
            full_reply.append(chunk["reply"])
        elif "error" in chunk:
            return chunk["error"]
    return "".join(full_reply)
