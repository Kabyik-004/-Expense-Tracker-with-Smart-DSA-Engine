import re
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "food": ["food", "restaurant", "dining", "lunch", "dinner", "breakfast", "pizza", "burger", "groceries", "zomato", "swiggy"],
    "transport": ["transport", "fuel", "petrol", "diesel", "uber", "ola", "cab", "bus", "train", "metro", "auto", "travel"],
    "shopping": ["shopping", "cloth", "amazon", "flipkart", "mall", "electronics", "gadget"],
    "entertainment": ["entertainment", "movie", "netflix", "spotify", "game", "concert", "ticket"],
    "bills": ["bill", "electricity", "water", "gas", "internet", "phone", "recharge", "rent"],
    "health": ["health", "doctor", "hospital", "medicine", "pharmacy", "gym", "fitness"],
    "education": ["education", "course", "book", "tution", "fee", "university", "college"],
}

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9,
    "oct": 10, "nov": 11, "dec": 12,
}


def _extract_amount(text):
    patterns = [
        r"(?:rs|inr|rupees?|₹)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:rs|inr|rupees?|₹)",
        r"(?:\$)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:dollars|usd)",
        r"(?:worth|valued?\s*at?)\s*([\d,]+(?:\.\d{1,2})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                continue
    return None


def _extract_category(text):
    lower = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                return cat
    return None


def _extract_description(text):
    stopwords = {"show", "list", "get", "tell", "give", "me", "my", "the", "a", "an", "i", "we"}
    cleaned = re.sub(r"(?:rs|inr|rupees?|₹)\s*[\d,]+(?:\.\d{1,2})?", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"[\d,]+(?:\.\d{1,2})?\s*(?:rs|inr|rupees?)", "", cleaned, flags=re.IGNORECASE)
    words = cleaned.split()
    meaningful = [w for w in words if w.lower() not in stopwords and len(w) > 2]
    return " ".join(meaningful).strip()[:120] if meaningful else None


def _extract_date(text):
    lower = text.lower()
    now = datetime.now(timezone.utc)
    today = now.date()

    if re.search(r"\btoday\b", lower):
        return today.isoformat()
    if re.search(r"\byesterday\b", lower):
        return (today - timedelta(days=1)).isoformat()
    if re.search(r"\bthis\s*month\b", lower):
        return today.isoformat()
    if re.search(r"\blast\s*month\b", lower):
        first = today.replace(day=1) - timedelta(days=1)
        return first.replace(day=1).isoformat()

    match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

    match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", text)
    if match:
        d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if y < 100:
            y += 2000
        return f"{y:04d}-{m:02d}-{d:02d}"

    for name, num in MONTH_NAMES.items():
        if re.search(r"\b" + re.escape(name) + r"\b", lower):
            if re.search(r"\blast\s+" + re.escape(name) + r"\b", lower):
                y = today.year - 1 if num > today.month else today.year
            else:
                y = today.year if num <= today.month else today.year - 1
            return f"{y:04d}-{num:02d}-01"

    return None


def _extract_source(text):
    sources = ["salary", "freelance", "business", "rental", "investment", "gift", "refund", "bonus", "interest", "dividend"]
    lower = text.lower()
    for src in sources:
        if re.search(r"\b" + re.escape(src) + r"\b", lower):
            return src
    return None


def extract_entities(message):
    if not message:
        return {}
    return {
        "amount": _extract_amount(message),
        "category": _extract_category(message),
        "description": _extract_description(message),
        "date": _extract_date(message),
        "source": _extract_source(message),
    }
