import json
import logging
import os
import re

from flask import current_app

from app.assistant.gemini_provider import chat

logger = logging.getLogger(__name__)

PAYMENT_KEYWORDS = {
    "upi": ["upi", "gpay", "google pay", "phonepe", "paytm", "bhim"],
    "card": ["card", "credit card", "debit card", "visa", "mastercard"],
    "bank_transfer": ["bank transfer", "neft", "rtgs", "imps", "transfer"],
    "cash": ["cash", "currency", "notes"],
}

CATEGORY_KEYWORDS = {
    "food": ["food", "restaurant", "pizza", "burger", "lunch", "dinner", "breakfast", "groceries", "zomato", "swiggy", "dining"],
    "transport": ["transport", "fuel", "petrol", "uber", "ola", "cab", "bus", "train", "metro", "auto", "travel"],
    "shopping": ["shopping", "amazon", "flipkart", "cloth", "mall", "electronics"],
    "entertainment": ["movie", "netflix", "spotify", "game", "concert", "ticket", "cinema"],
    "bills": ["bill", "electricity", "water", "gas", "internet", "phone", "recharge", "rent"],
    "health": ["doctor", "hospital", "medicine", "pharmacy", "gym", "clinic"],
    "education": ["course", "book", "fee", "university", "college", "tution"],
}

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9,
    "oct": 10, "nov": 11, "dec": 12,
}

EXTRACTION_PROMPT = """Extract financial transaction details from the user's message.

Return ONLY valid JSON. No markdown, no explanation.

Fields to extract (use null if not present):
- amount: number (the monetary value, without currency symbol)
- category: string or null (food, transport, shopping, entertainment, bills, health, education, or null)
- merchant: string or null (the business or vendor name)
- payment_method: string or null (upi, card, cash, bank_transfer, or null)
- date: string or null (YYYY-MM-DD format, or "today", "yesterday")
- notes: string or null (any additional context like "for dinner", "weekly groceries")

Rules:
- Do NOT guess or make up values. If a field is not mentioned, return null.
- Extract ONLY what is explicitly stated or clearly implied.
- For amount, extract the numeric value only (e.g., 450 not ₹450).
- For date, use "today" or "yesterday" if relative, or YYYY-MM-DD if absolute.

User message: {message}

Respond: {{"amount": null, "category": null, "merchant": null, "payment_method": null, "date": null, "notes": null}}"""


def _get_api_key():
    try:
        return current_app.config.get("GEMINI_API_KEY", "")
    except RuntimeError:
        return os.getenv("GEMINI_API_KEY", "")


def _regex_extract(message):
    result = {"amount": None, "category": None, "merchant": None, "payment_method": None, "date": None, "notes": None}
    lower = message.lower()

    amount_patterns = [
        r"(?:rs|inr|rupees?|\u20b9)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:rs|inr|rupees?|\u20b9)",
        r"(?:\$)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:dollars|usd)",
        r"\b(?:spent|paid|cost|worth|spend|buy|bought|earned|received|income)\s+(?:rs|inr|rupees?|\u20b9)?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:rs|inr|rupees?|\u20b9)?\s*([\d,]+(?:\.\d{1,2})?)\s+(?:rupees|rs|inr)\b",
    ]
    for p in amount_patterns:
        m = re.search(p, message, re.IGNORECASE)
        if m:
            result["amount"] = float(m.group(1).replace(",", ""))
            break

    if result["amount"] is None:
        bare = re.findall(r"\b(\d{2,6}(?:\.\d{1,2})?)\b", message)
        spending_words = re.search(r"\b(spent|paid|spend|cost|buy|bought|purchase|earned|received|income|salary|subscription|bill|fee|charge|payment)\b", lower)
        if bare and spending_words:
            result["amount"] = float(bare[-1].replace(",", ""))
        elif bare and len(bare) == 1 and re.search(r"(?:via|through|using|by)\s+(?:card|upi|cash|pay)", lower):
            result["amount"] = float(bare[-1].replace(",", ""))

    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(k) + r"\b", lower) for k in kws):
            result["category"] = cat
            break

    for known in ["Netflix", "Amazon", "Flipkart", "Swiggy", "Zomato", "Uber", "Ola", "Pizza Hut", "Dominos", "Pizza"]:
        if re.search(r"\b" + re.escape(known) + r"\b", message):
            result["merchant"] = known
            break

    if result["merchant"] is None:
        merchant_patterns = [
            r"(?:at|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
            r"(?:via|through|using)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
        ]
        for p in merchant_patterns:
            m = re.search(p, message)
            if m:
                candidate = m.group(1).strip()
                if candidate.lower() not in ("cash", "upi", "card", "bank", "online"):
                    result["merchant"] = candidate
                    break

    for method, kws in PAYMENT_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(k) + r"\b", lower) for k in kws):
            result["payment_method"] = method
            break

    if re.search(r"\byesterday\b", lower):
        result["date"] = "yesterday"
    elif re.search(r"\btoday\b", lower):
        result["date"] = "today"
    elif re.search(r"\bthis\s*month\b", lower):
        result["date"] = "this month"
    else:
        months_alt = "|".join(MONTH_NAMES)
        date_patterns = [
            r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b",
            r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b",
            r"\b(\d{1,2})[stndrd]{0,2}\s+(?:" + months_alt + r")\s+(\d{4})\b",
        ]
        for p in date_patterns:
            m = re.search(p, message, re.IGNORECASE)
            if m:
                result["date"] = m.group(0)
                break

    noise = r"(?:yesterday|today|via|through|using|upi|card|cash|bank|gpay|phonepe|paytm)"
    notes_candidates = re.findall(
        r"(?:for|for my|for the|to pay for)\s+(.+?)(?:\.|$|\s+(?:" + noise + r"|\d+))",
        message, re.IGNORECASE,
    )
    for nc in notes_candidates:
        cleaned = nc.strip().rstrip(".,!?;:")
        words = cleaned.split()
        cleaned_words = [w for w in words if not re.match(r"^\d+(?:\.\d{1,2})?$", w) and w.lower() not in ("yesterday", "today", "via", "through", "using", "upi", "card", "cash")]
        if cleaned_words and len(cleaned) > 2:
            result["notes"] = " ".join(cleaned_words)
            break

    if result["notes"] is None:
        desc_match = re.search(r"(?:on|at)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)", message)
        if desc_match:
            candidate = desc_match.group(1).strip().rstrip(".,!?;:")
            if candidate and not re.match(r"^\d+(?:\.\d{1,2})?$", candidate) and len(candidate) > 2:
                result["notes"] = candidate

    return result


def extract_entities(message):
    if not message or not message.strip():
        return {"amount": None, "category": None, "merchant": None, "payment_method": None, "date": None, "notes": None}

    api_key = _get_api_key()

    if api_key:
        try:
            prompt = EXTRACTION_PROMPT.format(message=message.strip())
            raw = chat(api_key, "", prompt)
            if raw:
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = re.sub(r"^```(?:json)?\s*", "", raw)
                    raw = re.sub(r"\s*```$", "", raw)
                result = json.loads(raw)
                validated = {k: result.get(k, None) for k in ("amount", "category", "merchant", "payment_method", "date", "notes")}
                return validated
        except Exception as e:
            logger.warning("Gemini extraction failed, falling back to regex: %s", e)

    return _regex_extract(message)
