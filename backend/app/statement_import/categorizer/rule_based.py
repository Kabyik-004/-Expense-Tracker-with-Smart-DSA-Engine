import re

from app.statement_import.categorizer.base import BaseCategorizer, CategorizationResult


RULES = [
    {"priority": 100, "keywords": ["salary", "payroll", "monthly pay"], "category": "Income", "exact": False},
    {"priority": 90, "keywords": ["zomato", "swiggy", "foodpanda", "eat sure", "box8"], "category": "Food & Dining", "exact": False},
    {"priority": 90, "keywords": ["amazon", "flipkart", "myntra", "ajio", "nykaa", "meesho"], "category": "Shopping", "exact": False},
    {"priority": 85, "keywords": ["uber", "uber india", "ola", "rapido", "meru"], "category": "Transportation", "exact": False},
    {"priority": 85, "keywords": ["irctc", "makemytrip", "ixigo", "goibibo", "ease my trip", "cleartrip", "yatra"], "category": "Transportation", "exact": False},
    {"priority": 85, "keywords": ["netflix", "prime video", "hotstar", "sony liv", "jiotv", "zee5", "voot", "disney+", "spotify", "gaana", "wynk"], "category": "Entertainment", "exact": False},
    {"priority": 80, "keywords": ["electricity", "power grid", "torrent power", "tata power", "bses", "adani electricity"], "category": "Bills & Utilities", "exact": False},
    {"priority": 80, "keywords": ["water bill", "jal board", "water tax"], "category": "Bills & Utilities", "exact": False},
    {"priority": 80, "keywords": ["broadband", "airtel fiber", "jio fiber", "hathway", "act fibernet", "internet bill"], "category": "Bills & Utilities", "exact": False},
    {"priority": 80, "keywords": ["rent", "rent pay", "rental"], "category": "Rent", "exact": False},
    {"priority": 75, "keywords": ["bigbasket", "grofers", "blinkit", "zepto", "instamart", "jiomart"], "category": "Groceries", "exact": False},
    {"priority": 75, "keywords": ["d mart", "reliance fresh", "more supermarket", "spencers"], "category": "Groceries", "exact": False},
    {"priority": 70, "keywords": ["medicare", "apollo pharmacy", "medlife", "pharmeasy", "netmeds", "1mg"], "category": "Health", "exact": False},
    {"priority": 70, "keywords": ["hospital", "clinic", "doctor", "diagnostic"], "category": "Health", "exact": False},
    {"priority": 60, "keywords": ["udemy", "coursera", "byju", "unacademy", "vedantu", "skillshare"], "category": "Education", "exact": False},
    {"priority": 60, "keywords": ["fuel", "petrol", "indian oil", "hp petrol", "bharat petroleum", "shell"], "category": "Transportation", "exact": False},
    {"priority": 50, "keywords": ["upi", "neft", "imps", "rtgs", "bank transfer", "fund transfer"], "category": "Transfer", "exact": False},
    {"priority": 50, "keywords": ["commission", "service fee", "processing fee", "convenience fee"], "category": "Bills & Utilities", "exact": False},
    {"priority": 40, "keywords": ["lunch", "breakfast", "dinner", "cafe", "restaurant", "hotel", "mess"], "category": "Food & Dining", "exact": False},
    {"priority": 40, "keywords": ["pizza hut", "dominos", "mcdonald", "kfc", "burger king", "subway", "taco bell"], "category": "Food & Dining", "exact": False},
]

CATEGORY_ALIASES = {
    "food": "Food & Dining",
    "dining": "Food & Dining",
    "shopping": "Shopping",
    "travel": "Transportation",
    "transport": "Transportation",
    "movie": "Entertainment",
    "entertainment": "Entertainment",
    "bills": "Bills & Utilities",
    "utility": "Bills & Utilities",
    "utilities": "Bills & Utilities",
    "health": "Health",
    "medical": "Health",
    "education": "Education",
    "rent": "Rent",
    "groceries": "Groceries",
    "grocery": "Groceries",
    "income": "Income",
    "salary": "Income",
    "transfer": "Transfer",
    "other": "Other",
    "uncategorized": "Other",
}


def resolve_category_alias(name):
    key = name.strip().lower()
    return CATEGORY_ALIASES.get(key, name)


def normalize(desc):
    if not desc:
        return ""
    return re.sub(r"[^a-z0-9\s]", " ", desc.lower()).strip()


def count_keyword_matches(description_normalized, keyword_normalized):
    if keyword_normalized in description_normalized:
        return 1
    keyword_tokens = set(keyword_normalized.split())
    desc_tokens = set(description_normalized.split())
    if keyword_tokens and keyword_tokens.intersection(desc_tokens):
        return 1
    return 0


class RuleBasedCategorizer(BaseCategorizer):

    def categorize(self, description):
        desc_normalized = normalize(description)
        if not desc_normalized:
            return CategorizationResult(
                category_name="Other",
                confidence=1.0,
                method="rule",
            )

        best_rule = None
        for rule in sorted(RULES, key=lambda r: r["priority"], reverse=True):
            for keyword in rule["keywords"]:
                kw_normalized = normalize(keyword)
                if kw_normalized in desc_normalized:
                    if best_rule is None or rule["priority"] > best_rule["priority"]:
                        best_rule = rule
                    break

        if best_rule:
            category = resolve_category_alias(best_rule["category"])
            confidence = min(0.95, best_rule["priority"] / 100.0)
            return CategorizationResult(
                category_name=category,
                confidence=round(confidence, 2),
                method="rule",
            )

        return CategorizationResult(
            category_name="Other",
            confidence=0.3,
            method="rule",
        )

    def categorize_batch(self, descriptions):
        return [self.categorize(desc) for desc in descriptions]

    @staticmethod
    def get_known_categories():
        seen = set()
        result = []
        for rule in RULES:
            cat = resolve_category_alias(rule["category"])
            if cat not in seen:
                seen.add(cat)
                result.append(cat)
        return sorted(result)

    @staticmethod
    def add_rule(priority, keywords, category):
        RULES.append({
            "priority": priority,
            "keywords": keywords if isinstance(keywords, list) else [keywords],
            "category": category,
        })
