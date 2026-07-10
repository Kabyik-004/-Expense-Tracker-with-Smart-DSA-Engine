import logging
import re

from app.assistant.extractor import extract_entities

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "add_expense": ["amount", "category"],
    "add_income": ["amount", "category"],
    "delete_expense": ["expense_id"],
    "update_expense": ["expense_id"],
}

OPTIONAL_FIELDS = {
    "add_expense": ["date", "payment_method", "notes", "merchant"],
    "add_income": ["date", "source", "notes"],
    "delete_expense": [],
    "update_expense": [],
}

ALL_FIELDS = {
    "add_expense": ["amount", "category", "date", "payment_method", "notes", "merchant"],
    "add_income": ["amount", "category", "date", "source", "notes"],
    "delete_expense": ["expense_id"],
    "update_expense": ["expense_id"],
}

CONVERSATION_ORDER = {
    "add_expense": ["category", "payment_method", "date"],
    "add_income": ["category", "date", "source"],
    "delete_expense": ["expense_id"],
    "update_expense": ["expense_id"],
}

QUESTIONS = {
    "amount": "What is the amount?",
    "category": "What category?",
    "date": "What date?",
    "payment_method": "Payment method?",
    "notes": "Any notes for this transaction?",
    "merchant": "Where did you make this purchase?",
    "source": "What is the source of this income?",
    "expense_id": "What is the expense ID?",
}

SUMMARY_VERBS = {
    "add_expense": "adding expense",
    "add_income": "adding income",
    "delete_expense": "deleting expense",
    "update_expense": "updating expense",
}


def get_missing_fields(intent, entities):
    required = REQUIRED_FIELDS.get(intent, [])
    order = CONVERSATION_ORDER.get(intent, [])

    required_have_all = all(entities.get(f) is not None for f in required)

    if required_have_all:
        field_order = [f for f in order if entities.get(f) is None]
    else:
        field_order = [f for f in required if entities.get(f) is None]

    return field_order


def get_next_question(missing_fields, field_index=0):
    if not missing_fields or field_index >= len(missing_fields):
        return None
    field = missing_fields[field_index]
    return QUESTIONS.get(field, f"Please provide {field}?")


def merge_entities_into_session(session_entities, new_entities):
    merged = dict(session_entities)
    for k, v in new_entities.items():
        if v is not None:
            merged[k] = v
    return merged


CATEGORY_KEYWORDS = {
    "food": ["food", "restaurant", "lunch", "dinner", "breakfast", "groceries", "pizza", "zomato", "swiggy", "dining", "eat"],
    "transport": ["transport", "fuel", "petrol", "uber", "ola", "cab", "bus", "train", "metro", "auto", "travel", "gas"],
    "shopping": ["shopping", "amazon", "flipkart", "cloth", "mall", "electronics", "store"],
    "entertainment": ["movie", "netflix", "spotify", "game", "concert", "ticket", "cinema", "entertainment"],
    "bills": ["bill", "electricity", "water", "gas", "internet", "phone", "recharge", "rent", "bills"],
    "health": ["doctor", "hospital", "medicine", "pharmacy", "gym", "clinic", "health"],
    "education": ["course", "book", "books", "fee", "university", "college", "tution", "education"],
}

PAYMENT_KEYWORDS = {
    "upi": ["upi", "gpay", "google pay", "phonepe", "paytm", "bhim"],
    "card": ["card", "credit card", "debit card", "visa", "mastercard", "credit", "debit"],
    "cash": ["cash", "currency", "notes", "physical"],
    "bank_transfer": ["bank transfer", "neft", "rtgs", "imps", "transfer", "net banking"],
}

DATE_KEYWORDS = {
    "today": ["today"],
    "yesterday": ["yesterday"],
    "this month": ["this month"],
    "last month": ["last month"],
}


def extract_from_slot_answer(message, field_name):
    entities = extract_entities(message)
    lower = message.lower().strip()

    if entities.get("amount") is None:
        numbers = re.findall(r"\b(\d+(?:\.\d{1,2})?)\b", message)
        if numbers:
            entities["amount"] = float(numbers[-1])

    if entities.get("category") is None and field_name == "category":
        for cat, kws in CATEGORY_KEYWORDS.items():
            if lower in kws:
                entities["category"] = cat
                break
        if entities.get("category") is None and len(lower.split()) <= 3:
            entities["category"] = lower

    if entities.get("payment_method") is None and field_name == "payment_method":
        for method, kws in PAYMENT_KEYWORDS.items():
            if lower in kws:
                entities["payment_method"] = method
                break

    if entities.get("date") is None and field_name == "date":
        for val, alts in DATE_KEYWORDS.items():
            if lower in alts:
                entities["date"] = val
                break
        if entities.get("date") is None:
            matched = re.findall(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", message)
            if matched:
                m = matched[0]
                if m[2]:
                    entities["date"] = f"{m[2]}-{m[1].zfill(2)}-{m[0].zfill(2)}"
                else:
                    entities["date"] = f"{m[1].zfill(2)}-{m[0].zfill(2)}"

    return entities


def build_summary(intent, entities):
    summary_verb = SUMMARY_VERBS.get(intent, intent.replace("_", " "))
    parts = []
    if entities.get("amount"):
        parts.append(f"\u20b9{entities['amount']:,.0f}")
    if entities.get("category"):
        parts.append(f"on {entities['category']}")
    if entities.get("merchant"):
        parts.append(f"at {entities['merchant']}")
    if entities.get("payment_method"):
        parts.append(f"via {entities['payment_method']}")
    if entities.get("date"):
        parts.append(entities["date"])
    if entities.get("notes"):
        parts.append(f"({entities['notes']})")
    detail = " ".join(parts) if parts else ""
    return f"Now executing: {summary_verb} {detail}".strip()
