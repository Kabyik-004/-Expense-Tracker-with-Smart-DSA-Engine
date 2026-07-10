import json
import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL = "gemini-2.0-flash"


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


def stream_chat(api_key, system_prompt, message, history=None):
    if not api_key:
        logger.error("GEMINI_API_KEY not configured")
        yield {"error": "AI assistant is not configured. Please set GEMINI_API_KEY."}
        return

    url = f"{BASE_URL}/{MODEL}:streamGenerateContent?alt=sse&key={api_key}"

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

    logger.debug("Sending request to Gemini API (%s)", MODEL)

    try:
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

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        body = e.response.text if e.response is not None else ""
        logger.error("Gemini HTTP %d: %s", status, body)
        if status == 403:
            yield {"error": "Invalid or expired API key. Please check GEMINI_API_KEY."}
        elif status == 429:
            yield {"error": "Rate limited. Please wait a moment and try again."}
        else:
            yield {"error": f"AI service error (HTTP {status}). Please try again."}

    except requests.exceptions.ConnectionError:
        logger.error("Gemini connection failed")
        yield {"error": "Could not connect to the AI service. Check your internet connection."}

    except requests.exceptions.Timeout:
        logger.error("Gemini request timed out")
        yield {"error": "AI service took too long to respond. Please try again."}

    except Exception as e:
        logger.exception("Gemini streaming failed")
        yield {"error": "An unexpected error occurred. Please try again."}


def chat(api_key, system_prompt, message, history=None):
    full_reply = []
    for chunk in stream_chat(api_key, system_prompt, message, history):
        if "reply" in chunk:
            full_reply.append(chunk["reply"])
        elif "error" in chunk:
            return chunk["error"]
    return "".join(full_reply)
