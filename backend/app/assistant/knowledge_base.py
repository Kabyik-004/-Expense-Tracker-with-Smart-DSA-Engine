import re
import logging

logger = logging.getLogger(__name__)

KNOWLEDGE_ENTRIES = [
    {
        "id": "calendar",
        "title": "Calendar Feature",
        "keywords": [
            "calendar", "where is calendar", "calendar view", "calendar page",
            "date picker", "date view", "month view", "spending calendar",
        ],
        "answer": (
            "There is no dedicated Calendar page in this app. "
            "Instead, you can ask me about any date or time period conversationally! "
            "For example, try:\n"
            "- 'What did I spend last month?'\n"
            "- 'Show my expenses from January'\n"
            "- 'How much did I spend this week?'\n"
            "- 'What were my expenses yesterday?'\n\n"
            "I'll fetch your spending data for that period using the analytics engine."
        ),
    },
    {
        "id": "import_statement",
        "title": "Import Bank Statement",
        "keywords": [
            "import", "statement", "bank statement", "upload statement",
            "import statement", "csv", "pdf", "excel", "how to import",
            "upload", "smart import", "bank",
        ],
        "answer": (
            "You can import bank statements through the Smart Import section. "
            "The supported file formats are CSV, PDF, and Excel (.xlsx/.xls). "
            "Maximum file size is 15 MB.\n\n"
            "Supported banks for auto-detection:\n"
            "- HDFC Bank (CSV)\n"
            "- ICICI Bank (CSV)\n"
            "- State Bank of India (CSV)\n"
            "- Axis Bank (CSV)\n"
            "- Kotak Mahindra Bank (CSV)\n"
            "- Yes Bank (CSV)\n\n"
            "The import flow is:\n"
            "1. Upload your statement file\n"
            "2. Preview the parsed transactions with auto-detected categories\n"
            "3. Confirm to import — each transaction becomes an expense or income record\n\n"
            "The system auto-categorizes transactions based on description keywords "
            "and detects duplicates using similarity matching."
        ),
    },
    {
        "id": "undo",
        "title": "Undo Feature",
        "keywords": [
            "undo", "how does undo work", "undo feature", "undo expense",
            "undo delete", "undo create", "undo update", "undo stack",
            "how to undo", "reverse", "rollback",
        ],
        "answer": (
            "The Undo feature tracks your last 10 operations (CREATE, UPDATE, DELETE) "
            "using a LIFO (Last-In-First-Out) stack built on a deque data structure.\n\n"
            "How it works:\n"
            "- CREATE: Stores a snapshot of nothing; undo deletes the created record\n"
            "- UPDATE: Stores a JSON snapshot of all old field values; undo restores them\n"
            "- DELETE: Stores the full deleted record; undo recreates it with original data\n\n"
            "Limits:\n"
            "- Maximum 10 undo operations per user (oldest auto-evicted)\n"
            "- Works for both expenses and income records\n\n"
            "You can check undo status anytime:\n"
            "- 'What can I undo?'\n"
            "- 'Undo my last action'"
        ),
    },
    {
        "id": "merge_sort",
        "title": "Merge Sort Algorithm",
        "keywords": [
            "merge sort", "sorting algorithm", "how are expenses sorted",
            "sort expenses", "sorting", "algorithm", "merge sort algorithm",
            "how does sorting work", "sorted by",
        ],
        "answer": (
            "This app uses Merge Sort — a classic divide-and-conquer sorting algorithm.\n\n"
            "How it works:\n"
            "1. Divide: Recursively split the array at the midpoint\n"
            "2. Conquer: Recursively sort both halves\n"
            "3. Combine: Merge the two sorted subarrays back together\n\n"
            "Performance:\n"
            "- Time Complexity: O(n log n) in all cases (best, average, worst)\n"
            "- Space Complexity: O(n) for temporary arrays during merge\n"
            "- Stable sort: maintains relative order of equal elements\n\n"
            "Where it's used:\n"
            "- Single-field sorting: by amount, date, category, or title\n"
            "- Multi-field sorting: leverages stability for compound sorts\n"
            "- Pre-sorting for binary search: sorts by ID or date before binary search "
            "to achieve O(log n) lookups\n\n"
            "For example, searching by date first sorts all expenses (O(n log n)), "
            "then finds dates in O(log n + k) time."
        ),
    },
    {
        "id": "expense_categorization",
        "title": "Expense Categorization",
        "keywords": [
            "categorization", "categories", "category", "how are expenses categorized",
            "expense categories", "category system", "how categories work",
            "auto categorization", "default categories",
        ],
        "answer": (
            "Expenses are organized into user-specific categories. "
            "Each user has their own set of categories that can include both "
            "default system categories and custom ones you create.\n\n"
            "Default categories include:\n"
            "- Food & Dining, Shopping, Transportation, Entertainment\n"
            "- Bills & Utilities, Rent, Groceries, Health, Education\n\n"
            "How categorization works:\n"
            "- Manually: When adding an expense, you pick a category\n"
            "- Auto-categorization: When importing bank statements, the system uses "
            "27 rule-based keyword patterns to suggest categories "
            "(e.g., 'zomato' → Food & Dining, 'uber' → Transportation)\n"
            "- Each category can have an icon (emoji), color (hex), "
            "and optional monthly budget limit\n\n"
            "You can view all your categories in the app's sidebar."
        ),
    },
    {
        "id": "analytics",
        "title": "Analytics Feature",
        "keywords": [
            "analytics", "how analytics works", "analytics feature",
            "analytics overview", "spending analysis", "insights",
            "how does analytics work", "trends", "spending patterns",
            "category analysis", "time series", "dashboard",
        ],
        "answer": (
            "The analytics engine provides four views of your financial data:\n\n"
            "1. Overview:\n"
            "   - Total expenses, total income, and balance\n"
            "   - Highest and lowest expense amounts\n"
            "   - Average expense per transaction\n\n"
            "2. Category Analysis:\n"
            "   - Most-used category (by count)\n"
            "   - Top 5 categories by total spending\n"
            "   - Full distribution with percentages\n\n"
            "3. Time Series:\n"
            "   - Daily, weekly, and monthly spending breakdowns\n"
            "   - Sorted chronologically for trend analysis\n\n"
            "4. Dashboard (combined view):\n"
            "   - All metrics in one place for a complete financial picture\n\n"
            "All analytics are computed from your own data only and "
            "can be accessed via the Analytics page or by asking me!\n"
            "- 'Show my dashboard'\n"
            "- 'What are my spending patterns?'\n"
            "- 'How much did I spend on food this month?'"
        ),
    },
    {
        "id": "budget",
        "title": "Budget Feature",
        "keywords": [
            "budget", "budgets", "budgeting", "how budgets work",
            "budget feature", "monthly budget", "budget limit",
            "budget status", "budget optimization",
        ],
        "answer": (
            "Budgets are set on a monthly basis, optionally tied to a specific category.\n\n"
            "How budgets work:\n"
            "- Each budget targets a specific (month, year, category) combination\n"
            "- A budget with no category = overall monthly spending cap\n"
            "- Only one budget per category per month (creating a new one updates the old)\n\n"
            "Budget Status:\n"
            "- Tracks how much you've spent vs your budget\n"
            "- Warning at 80% usage\n"
            "- Exceeded at 100%+ usage\n\n"
            "Budget Optimizer (DSA):\n"
            "- Uses a 0/1 Knapsack dynamic programming algorithm to suggest "
            "the optimal category allocation within your total budget\n"
            "- Also supports greedy allocation by priority\n\n"
            "You can view budgets on the Budgets page or ask me:\n"
            "- 'What's my budget status this month?'\n"
            "- 'How much budget do I have left for food?'"
        ),
    },
    {
        "id": "dsa_engine",
        "title": "DSA Engine (Data Structures & Algorithms)",
        "keywords": [
            "dsa", "data structures", "algorithms", "dsa engine",
            "smart dsa", "how does the app work internally",
            "hash table", "binary search", "linear search",
            "trie", "graph", "knapsack", "quick sort", "heap sort",
        ],
        "answer": (
            "This app is built with a Smart DSA Engine that powers performance-critical features.\n\n"
            "Data Structures:\n"
            "- HashTable (dict): O(1) in-memory aggregation for instant category totals, "
            "counts, and monthly summaries\n"
            "- Stack (deque): LIFO undo system, max 10 operations per user\n"
            "- Trie (prefix tree): Fast keyword search on expense titles and descriptions\n"
            "- Graph (adjacency list): Spending category co-occurrence analysis "
            "with BFS, DFS, and cluster detection\n"
            "- TTL Cache: In-memory user summary tables with 5-minute expiry\n\n"
            "Algorithms:\n"
            "- Merge Sort: O(n log n) stable sort for single/multi-field expense sorting\n"
            "- Quick Sort: Alternative sort with random pivot\n"
            "- Heap Sort: Sort using max-heap\n"
            "- Linear Search: O(n) substring search on title, description, category\n"
            "- Binary Search: O(log n) search on sorted ID and date fields\n"
            "- 0/1 Knapsack DP: Optimal budget allocation across categories\n"
            "- Greedy Allocation: Priority-based budget distribution\n"
            "- Jaccard Similarity: Duplicate transaction detection during imports"
        ),
    },
    {
        "id": "hash_table",
        "title": "HashTable Data Structure",
        "keywords": [
            "hash table", "hash table", "hashtable", "in-memory",
            "summary cache", "aggregation", "instant summary",
        ],
        "answer": (
            "The HashTable is a custom in-memory data structure used for instant "
            "expense aggregations — no database queries needed for summary views.\n\n"
            "Where it's used:\n"
            "- Category totals: total amount per category (O(1) lookup)\n"
            "- Category counts: number of expenses per category (O(1) lookup)\n"
            "- Monthly totals: total spending per month (O(1) lookup)\n\n"
            "When you create, update, or delete an expense, the HashTable is updated "
            "immediately (O(1) add/remove). This means summary pages load instantly "
            "without scanning all expenses."
        ),
    },
    {
        "id": "search_features",
        "title": "Search Features",
        "keywords": [
            "search", "how to search", "find expense", "look up expense",
            "search expense", "search by", "find",
        ],
        "answer": (
            "You can search expenses in several ways:\n\n"
            "1. By Title: Linear search, case-insensitive substring match\n"
            "2. By Description: Linear search, case-insensitive substring match\n"
            "3. By Category: Filter by category ID\n"
            "4. By ID: Binary search (after sorting) — O(log n) lookup\n"
            "5. By Date: Binary search — O(log n + k) for a specific date\n"
            "6. By Date Range: Binary range search\n"
            "7. Keyword Search: Uses a Trie (prefix tree) for fast autocomplete-like lookups\n\n"
            "The AI assistant can also search for you! Just ask:\n"
            "- 'Find my expense for Pizza'\n"
            "- 'Search for transactions at Amazon'\n"
            "- 'Show me what I spent on groceries'"
        ),
    },
    {
        "id": "authentication",
        "title": "Authentication & Security",
        "keywords": [
            "auth", "authentication", "login", "register", "signup",
            "password", "jwt", "token", "security", "logout",
            "change password", "forgot password", "profile",
        ],
        "answer": (
            "Authentication uses JWT (JSON Web Tokens) with access and refresh tokens.\n\n"
            "Features:\n"
            "- Register with username, email, and password\n"
            "- Login with email or username\n"
            "- Forgot password flow: email → OTP verification → reset password\n"
            "- Change password from profile settings\n"
            "- Upload avatar (base64, max 2MB)\n"
            "- View and edit profile details\n"
            "- Activity log of last 20 actions\n\n"
            "Password requirements:\n"
            "- Minimum 8 characters, maximum 128\n"
            "- Must include uppercase, lowercase, and a digit"
        ),
    },
]


def find_answer(message):
    if not message or not message.strip():
        return None

    lower = message.lower().strip()

    best_entry = None
    best_score = 0

    for entry in KNOWLEDGE_ENTRIES:
        score = _score_match(lower, entry)
        if score > best_score or (score == best_score and best_entry and len(entry["keywords"]) < len(best_entry["keywords"])):
            best_score = score
            best_entry = entry

    if best_score >= 0.3:
        logger.debug("Knowledge match: '%s' (score=%.2f) for: %.50s", best_entry["id"], best_score, message)
        return best_entry["answer"]

    return None


def _score_match(lower, entry):
    query_words = set(re.findall(r"[a-z]+", lower))
    if not query_words:
        return 0

    for keyword in entry["keywords"]:
        kw_lower = keyword.lower()
        if kw_lower in lower:
            kw_words = set(re.findall(r"[a-z]+", kw_lower))
            common = query_words & kw_words
            if common:
                overlap = len(common) / max(len(query_words), len(kw_words)) if query_words else 0
                if kw_lower == lower.strip() or lower.startswith(kw_lower):
                    return 1.0
                if kw_lower in lower:
                    phrase_bonus = 0.2 if len(kw_lower.split()) > 1 else 0
                    return min(1.0, max(0.7, overlap) + phrase_bonus)

    word_matches = 0
    for word in query_words:
        for keyword in entry["keywords"]:
            kw_words = set(re.findall(r"[a-z]+", keyword.lower()))
            if word in kw_words:
                word_matches += 1
                break

    if word_matches > 0 and query_words:
        return min(0.6, word_matches / len(query_words) * 0.8)

    return 0
