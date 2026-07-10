import json
import logging
import os
import re

from flask import current_app

from app.assistant.gemini_provider import chat

logger = logging.getLogger(__name__)

INTENTS = [
    "add_expense", "add_income", "delete_expense", "update_expense",
    "search_expense", "dashboard_query", "analytics_query",
    "navigation_help", "general_help", "calendar_query",
    "bank_statement_query", "unknown",
]

CLASSIFICATION_PROMPT = """You are an intent classifier for a personal finance app. Classify the user's message into exactly one intent and extract relevant entities.

Return ONLY valid JSON. No markdown, no explanation.

Intents:
- add_expense: User wants to record a new expense (spent, paid, bought, purchased)
- add_income: User wants to record new income (earned, received, salary, got paid)
- delete_expense: User wants to remove an existing expense
- update_expense: User wants to change an existing expense
- search_expense: User wants to find/ look up an expense (search, find, show me, where is)
- dashboard_query: User wants an overview or summary of their finances (dashboard, overview, how am I doing)
- analytics_query: User wants analysis, trends, or breakdowns (analytics, trends, patterns, category breakdown)
- navigation_help: User wants to go to a specific page or feature (take me to, open, navigate, show the page)
- general_help: User wants to know what the app can do (help, what can you do, how does this work)
- calendar_query: User is asking about dates, months, or time periods (this month, last week, in January)
- bank_statement_query: User wants to import or view bank statements (statement, bank statement, import statement)
- unknown: Message does not fit any of the above

Entities to extract (null if not found):
- amount: number (expense/income amounts)
- category: string (food, transport, shopping, entertainment, bills, health, education, etc.)
- description: string (what the transaction was for)
- date: string (YYYY-MM-DD, or "today", "yesterday", "this month")
- source: string (salary, freelance, business, etc. — for income)
- expense_id: number (for delete/update by ID)
- search_query: string (what the user is searching for)
- time_period: string (this week, last month, this year, etc.)
- target_page: string (dashboard, expenses, incomes, analytics, budgets, settings, import)
- date_range: string ("2025-01 to 2025-03", "last 30 days")
- month: number
- year: number

User message: {message}

Respond: {{"intent": "...", "confidence": 0.0-1.0, "entities": {{...}}}}"""


def _get_api_key():
    try:
        return current_app.config.get("GEMINI_API_KEY", "")
    except RuntimeError:
        return os.getenv("GEMINI_API_KEY", "")


def _regex_classify(message):
    lower = message.lower()

    if re.search(r"\b(statement|bank statement|import statement|csv|excel|pdf|upload)\b", lower):
        return "bank_statement_query", 0.7

    if re.search(r"\b(delete|remove|erase|cancel)\b.*\b(expense|transaction|entry|item)\b", lower):
        return "delete_expense", 0.8

    if re.search(r"\b(update|change|edit|modify|correct)\b.*\b(expense|transaction|entry|item)\b", lower):
        return "update_expense", 0.8

    if re.search(r"\b(earned|received|salary|income|credit|deposit|got paid|wage|bonus)\b", lower):
        return "add_income", 0.8

    is_question = bool(re.search(r"^(what|which|how|when|where|why|who|did|do|does|is|are|can|could|would)", lower))

    if not is_question and re.search(r"\b(?:spent|paid|bought|purchased)\b", lower) and re.search(r"\b\d+\b", lower):
        return "add_expense", 0.85

    if not is_question and re.search(r"\b(?:spent|paid|bought|purchased)\b", lower):
        return "add_expense", 0.7

    if re.search(r"\b(calendar|schedule|this month|last month|this week|last week|this year|in january|in february|in march|monthly)\b", lower):
        return "calendar_query", 0.7

    if re.search(r"\b(dashboard|overview|summary|how much|total balance|net worth|biggest|largest|highest|savings|overspend(?:ing)?|spending pattern|financial health|my balance|am i)\b", lower):
        return "dashboard_query", 0.7

    if re.search(r"\b(analytics|trend|pattern|breakdown|categor|distribution|insight|chart|graph|average daily|top category)\b", lower):
        return "analytics_query", 0.75

    if is_question and re.search(r"\b(spent|spend|paid|bought|purchased|expense|cost|pay|spending)\b", lower):
        if re.search(r"\b(today|yesterday|this week|this month|last month|this year|last week)\b", lower):
            return "calendar_query", 0.7
        return "search_expense", 0.7

    if re.search(r"\b(navigate|take me to|open|go to|show the page|redirect)\b", lower):
        return "navigation_help", 0.7

    if re.search(r"\b(search|find|look up|where is|show me)\b", lower):
        return "search_expense", 0.7

    if re.search(r"\b(help|guide|how|what can you|tutorial|commands|hi|hello|hey|greetings)\b", lower):
        return "general_help", 0.7

    return "unknown", 0.4


def _regex_extract_entities(message, intent):
    entities = {}

    amount_patterns = [
        r"(?:rs|inr|rupees?|\u20b9)\s*([\d,]+(?:\.\d{1,2})?)",
        r"([\d,]+(?:\.\d{1,2})?)\s*(?:rs|inr|rupees?|\u20b9)",
        r"(?:\$)\s*([\d,]+(?:\.\d{1,2})?)",
    ]
    for p in amount_patterns:
        m = re.search(p, message, re.IGNORECASE)
        if m:
            entities["amount"] = float(m.group(1).replace(",", ""))
            break

    category_keywords = {
        "food": ["food", "restaurant", "lunch", "dinner", "breakfast", "groceries", "pizza", "zomato", "swiggy"],
        "transport": ["transport", "fuel", "petrol", "uber", "ola", "cab", "bus", "train", "metro", "auto"],
        "shopping": ["shopping", "amazon", "flipkart", "cloth", "electronics"],
        "entertainment": ["movie", "netflix", "spotify", "game", "concert", "ticket"],
        "bills": ["bill", "electricity", "water", "internet", "phone", "recharge", "rent"],
        "health": ["doctor", "hospital", "medicine", "pharmacy", "gym"],
        "education": ["course", "book", "fee", "university", "college"],
    }
    lower = message.lower()
    for cat, kws in category_keywords.items():
        if any(re.search(r"\b" + re.escape(k) + r"\b", lower) for k in kws):
            entities["category"] = cat
            break

    desc_match = re.search(r"(?:for|on|at)\s+(.+?)(?:\.|$|\s+(?:yesterday|today|last|this))", message, re.IGNORECASE)
    if desc_match:
        entities["description"] = desc_match.group(1).strip()

    if re.search(r"\btoday\b", lower):
        entities["date"] = "today"
    elif re.search(r"\byesterday\b", lower):
        entities["date"] = "yesterday"

    source_keywords = ["salary", "freelance", "business", "rental", "investment", "gift", "refund", "bonus"]
    for s in source_keywords:
        if re.search(r"\b" + re.escape(s) + r"\b", lower):
            entities["source"] = s
            break

    id_match = re.search(r"(?:expense|id|#)\s*(\d+)", lower, re.IGNORECASE)
    if id_match:
        entities["expense_id"] = int(id_match.group(1))

    if intent == "search_expense":
        query = message.strip()
        for prefix in ["search", "find", "look up", "show me", "where is"]:
            query = re.sub(r"^" + re.escape(prefix), "", query, flags=re.IGNORECASE).strip()
        query = re.sub(r"\b(expense|transaction|entry)\b", "", query, flags=re.IGNORECASE).strip().strip("?.,!;:")
        if query:
            entities["search_query"] = query

    time_periods = {
        "this week": "this week", "last week": "last week",
        "this month": "this month", "last month": "last month",
        "this year": "this year", "last year": "last year",
        "today": "today", "yesterday": "yesterday",
    }
    for phrase, val in time_periods.items():
        if phrase in lower:
            entities["time_period"] = val
            break

    return entities


def classify_message(message):
    if not message or not message.strip():
        return {"intent": "unknown", "confidence": 0.0, "entities": {}}

    api_key = _get_api_key()

    if api_key:
        try:
            prompt = CLASSIFICATION_PROMPT.format(message=message.strip())
            raw = chat(api_key, "", prompt)
            if raw:
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = re.sub(r"^```(?:json)?\s*", "", raw)
                    raw = re.sub(r"\s*```$", "", raw)
                result = json.loads(raw)
                intent = result.get("intent", "unknown")
                confidence = float(result.get("confidence", 0.5))
                entities = result.get("entities", {})
                if intent in INTENTS:
                    return {"intent": intent, "confidence": min(confidence, 1.0), "entities": entities}
        except Exception as e:
            logger.warning("Gemini classification failed, falling back to regex: %s", e)

    intent, confidence = _regex_classify(message)
    entities = _regex_extract_entities(message, intent)
    return {"intent": intent, "confidence": confidence, "entities": entities}
