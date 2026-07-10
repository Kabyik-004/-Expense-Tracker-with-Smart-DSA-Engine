import re
import logging

logger = logging.getLogger(__name__)

PATTERNS = [
    ("greeting", r"\b(hi|hello|hey|good\s*morning|good\s*evening|sup|howdy|yo)\b"),
    ("help", r"\b(help|what can you do|commands|how\s*to|guide)\b"),
    ("add_expense", r"\b(spent|spend|paid|bought|purchased|transaction|expense|cost|used|swiped)\b"),
    ("list_expenses", r"\b(show\s*expenses|list\s*expenses|recent|all expenses|expense\s*list|transactions)\b"),
    ("get_summary", r"\b(summary|total|balance|how much|overview|financial|money|spending)\b"),
    ("add_income", r"\b(earned|received|salary|income|credit|deposit|got\s*paid|wage)\b"),
    ("list_incomes", r"\b(show\s*income|list\s*income|income\s*list|earnings)\b"),
    ("get_analytics", r"\b(analytics|trends|insight|breakdown|categor|categorize|distribution|chart|graph|pattern)\b"),
]


def detect_intent(message):
    lower = message.lower()
    for intent, pattern in PATTERNS:
        if re.search(pattern, lower):
            logger.debug("Intent '%s' matched for: %s", intent, message[:60])
            return intent
    logger.debug("No intent matched — defaulting to 'unknown'")
    return "unknown"
