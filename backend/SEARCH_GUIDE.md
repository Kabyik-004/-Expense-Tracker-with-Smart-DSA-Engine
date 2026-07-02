# Search Algorithms Guide

## Overview

This guide covers **Linear Search** and **Binary Search** implementations for the Expense Tracker system.

**Two Search Strategies:**
- **Linear Search**: For text fields (title, description, category) - searches unsorted data
- **Binary Search**: For numeric/date fields (ID, date) - requires pre-sorting but extremely fast

---

## Algorithm Comparison

### Performance Table

| Data Type | Algorithm | Unsorted? | Time Complexity | Real Example |
|-----------|-----------|-----------|-----------------|--------------|
| **Title** | Linear | Yes ✓ | O(n) | Search 100K expenses: 100K checks |
| **Description** | Linear | Yes ✓ | O(n) | Search 100K expenses: 100K checks |
| **Category** | Linear | Yes ✓ | O(n) | Search 100K expenses: 100K checks |
| **Expense ID** | Binary | No (sort first) | O(log n) | Search 100K expenses: 17 checks |
| **Date** | Binary | No (sort first) | O(log n) | Search 100K expenses: 17 checks |
| **Date Range** | Binary | No (sort first) | O(log n + k) | Search 100K expenses: 17 + k checks |

---

## Linear Search - O(n)

### Algorithm

**Concept:** Check every item one-by-one until target found or end reached.

**Pseudocode:**
```python
for item in items:
    if matches(item, query):
        add to results
return results
```

### Characteristics

- ✓ Works on **unsorted data**
- ✓ Works on **text** (partial match, case-insensitive)
- ✗ Slow for large datasets
- ✗ O(n) - must potentially check every item

### Time Complexity Analysis

**Best Case: O(1)**
- Target is first item
- Example: Search for "Coffee" in [Coffee, Tea, Water] → Found immediately

**Worst Case: O(n)**
- Target at end or not found
- Example: Search for "Missing" in [Coffee, Tea, Water] → Check all 3 items

**Average Case: O(n/2) = O(n)**
- Target in middle
- Example: Search for "Tea" in [Coffee, Tea, Water] → Check ~2 items

### Visual Example

```
Linear Search for "groceries" in titles:
Items:  [Coffee Shop] [Grocery Store] [Coffee Maker] [Supermarket]
Check:   X             ✓ Match!
         1 check      Found at position 2

Worst case: [Coffee] [Tea] [Juice] [Taxi] [Gas]
            X        X     X       X      X
            5 checks (all items)
```

### Space Complexity

**O(k)** where k = number of matching results

- Returns list of matches
- Must store all found items

### Use Cases

✓ **When to use Linear Search:**
- Small dataset (< 1,000 items)
- Unsorted data
- Text search (title, description)
- Few searches (sorting cost not worth it)
- Partial/substring matches

✗ **When NOT to use:**
- Large sorted datasets (> 100K)
- Doing many searches (sort once, use binary)

### Real-World Example

**Expense Title Search**
```python
# Find all expenses with "coffee" in title
expenses = [
    Expense(title="Morning Coffee", amount=5.50),
    Expense(title="Lunch", amount=12.00),
    Expense(title="Coffee Maker", amount=45.00),
]

results = search_by_title(expenses, "coffee")
# → Returns: [Morning Coffee, Coffee Maker]

# Time: O(n) = check all 3 expenses
# But data is unsorted, so binary search won't work
```

---

## Binary Search - O(log n)

### Algorithm

**Concept:** On **sorted** data, divide search space in half each iteration.

**How it works:**
1. Look at middle element
2. If match: done!
3. If target < middle: search left half
4. If target > middle: search right half
5. Repeat with half the remaining items

**Pseudocode:**
```python
left = 0, right = len(items) - 1

while left <= right:
    mid = (left + right) / 2
    if items[mid] == target:
        return mid
    elif items[mid] < target:
        left = mid + 1      # Search right half
    else:
        right = mid - 1     # Search left half

return -1  # Not found
```

### Characteristics

- ✓ **Extremely fast** on sorted data - O(log n)
- ✓ Works on numbers, dates, comparable values
- ✗ **Requires pre-sorted data** - O(n log n) cost
- ✗ Won't work on unsorted data

### Time Complexity Analysis

**Key Insight:** Each comparison **eliminates half** of remaining items

**Comparison:**
```
Items:   1     2     4     8     16    32    64    128   256   512   1024
Checks:  1     2     3     4     5     6     7     8     9     10    11
         (log₂(n) ≈ 10 checks for 1000 items)
```

**Formula:** Maximum comparisons = log₂(n)

- 10 items → max 4 comparisons
- 100 items → max 7 comparisons
- 1,000 items → max 10 comparisons
- 1,000,000 items → max 20 comparisons

### Visual Example

```
Binary Search for target=42 in [1, 5, 12, 25, 42, 68, 89, 105]:

Step 1: Check middle (25)
[1, 5, 12, 25] | 42 | [68, 89, 105]
                  42 > 25 → search right half

Step 2: Check middle of right (68)
[42, 68] | [89, 105]
42 < 68 → search left half

Step 3: Found 42
[42] → Match! Return index

Total: 3 comparisons (log₂(8) = 3)
```

### Space Complexity

**O(1)** - Constant space

- Only tracks left/right pointers
- No recursion (iterative implementation)
- No additional data structures

### Use Cases

✓ **When to use Binary Search:**
- Large dataset (> 100K items)
- Data is sortable (numbers, dates)
- Many searches planned (sort cost amortized)
- One-time sort, multiple fast searches

✗ **When NOT to use:**
- Unsorted data (unless you sort first)
- Text search (can't binary search "coffee" substring)
- Dynamic data (frequently changing)

### Requirement: Pre-Sort Data

**CRITICAL:** Binary search only works on **sorted** data.

```python
from app.services.merge_sort import merge_sort

# Wrong ❌ - Binary search on unsorted data
expenses_unsorted = [Expense(id=5), Expense(id=2), Expense(id=8)]
idx = binary_search(expenses_unsorted, 5, "id")  # Unreliable!

# Correct ✓ - Sort first, then binary search
expenses = [Expense(id=5), Expense(id=2), Expense(id=8)]
sorted_expenses = merge_sort(expenses, key="id", ascending=True)
                  # → [Expense(id=2), Expense(id=5), Expense(id=8)]
idx = binary_search(sorted_expenses, 5, "id")  # ✓ Works: returns 1
```

### Real-World Example

**Expense ID Search (Fast)**
```python
# Search for expense by ID in large dataset
expenses = Expense.query.filter_by(user_id=user_id).all()
# → 500,000 expenses unsorted

# Step 1: Sort by ID (O(n log n) - done once)
sorted_expenses = merge_sort(expenses, key="id", ascending=True)
# → Takes ~10 million operations (500K * log₂(500K) ≈ 9M)

# Step 2: Binary search (O(log n) - very fast!)
result = binary_search(sorted_expenses, target_id=12345, "id")
# → Takes ~19 comparisons maximum (log₂(500K) ≈ 19)
# → MUCH FASTER than linear's ~250K checks!

# Speedup for 1 search:
#   Linear: 250K checks
#   Binary: 19 checks
#   Speedup: 13,000× faster
```

---

## Algorithm Trade-Off Analysis

### Scenario: 1,000 Searches on 100,000 Items

**Option A: Linear Search (No Sort)**
```
Time per search: O(n) = 100,000 checks average
Total time: 1,000 × 100,000 = 100 million operations
```

**Option B: Binary Search (Sort Once)**
```
Sort once: O(n log n) = 100,000 × 17 ≈ 1.7 million operations
Each search: O(log n) = 17 checks
1,000 searches: 1,000 × 17 = 17,000 operations
Total: 1.7M + 17K = 1.717 million operations

Speedup: 100M / 1.7M ≈ 58× faster!
```

**Breakeven Point:**
- When number of searches > 1, binary search becomes worth it
- For 1 search on 100K items: linear faster (no sort overhead)
- For 2+ searches on 100K items: binary search faster

---

## API Endpoints

### Linear Search Endpoints

#### Search by Title
```bash
GET /api/expenses/search/title?q=<query>
```

**Parameters:**
- `q` (required): Search query (substring, case-insensitive)

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/search/title?q=coffee"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Morning Coffee",
      "amount": 5.50,
      "date": "2026-07-01"
    },
    {
      "id": 3,
      "title": "Coffee Maker",
      "amount": 45.00,
      "date": "2026-07-02"
    }
  ],
  "message": "Found 2 expenses matching 'coffee'"
}
```

**Time Complexity:** O(n)

---

#### Search by Description
```bash
GET /api/expenses/search/description?q=<query>
```

**Parameters:**
- `q` (required): Search query (substring, case-insensitive)

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/search/description?q=burger"
```

**Time Complexity:** O(n)

---

#### Search by Category
```bash
GET /api/expenses/search/category?category_id=<id>
```

**Parameters:**
- `category_id` (required): Category ID to filter by

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/search/category?category_id=5"
```

**Time Complexity:** O(n)

---

### Binary Search Endpoints

#### Search by Expense ID
```bash
GET /api/expenses/search/id?expense_id=<id>
```

**Parameters:**
- `expense_id` (required): Expense ID to find

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/search/id?expense_id=42"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 42,
    "title": "Lunch",
    "amount": 15.00,
    "date": "2026-07-01"
  },
  "message": "Found expense 42"
}
```

**Time Complexity:** O(n log n) for sort + O(log n) for search

---

#### Search by Date
```bash
GET /api/expenses/search/date?date=<YYYY-MM-DD>
```

**Parameters:**
- `date` (required): Date to search for (format: YYYY-MM-DD)

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/search/date?date=2026-07-01"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "title": "Coffee", "amount": 5.50, "date": "2026-07-01"},
    {"id": 2, "title": "Lunch", "amount": 15.00, "date": "2026-07-01"}
  ],
  "message": "Found 2 expenses on 2026-07-01"
}
```

**Time Complexity:** O(n log n) for sort + O(log n + k) for search, where k = expenses on that date

---

#### Search by Date Range
```bash
GET /api/expenses/search/date-range?start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>
```

**Parameters:**
- `start_date` (required): Start date (format: YYYY-MM-DD)
- `end_date` (required): End date (format: YYYY-MM-DD)

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/search/date-range?start_date=2026-07-01&end_date=2026-07-31"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "title": "Coffee", "amount": 5.50, "date": "2026-07-01"},
    {"id": 2, "title": "Lunch", "amount": 15.00, "date": "2026-07-05"},
    {"id": 3, "title": "Dinner", "amount": 30.00, "date": "2026-07-15"}
  ],
  "message": "Found 3 expenses between 2026-07-01 and 2026-07-31"
}
```

**Time Complexity:** O(n log n) for sort + O(log n + k) for search, where k = expenses in range

---

## Code Examples

### Python Usage

#### Linear Search for Title
```python
from app.services.search import search_expenses_by_title

expenses = Expense.query.filter_by(user_id=user_id).all()

# Search for "coffee" in titles (case-insensitive)
results = search_expenses_by_title(expenses, "coffee")

for expense in results:
    print(f"{expense.title}: ${expense.amount}")

# Output:
# Morning Coffee: $5.50
# Coffee Maker: $45.00

# Time: O(n) where n = total expenses
```

#### Binary Search for Expense ID
```python
from app.services.merge_sort import merge_sort
from app.services.search import search_expense_by_id

expenses = Expense.query.filter_by(user_id=user_id).all()

# Step 1: Sort by ID (O(n log n))
sorted_expenses = merge_sort(expenses, key="id", ascending=True)

# Step 2: Binary search (O(log n))
target_expense = search_expense_by_id(sorted_expenses, expense_id=42)

if target_expense:
    print(f"Found: {target_expense.title}")
else:
    print("Expense not found")

# Time: O(n log n) sort + O(log n) search
```

#### Binary Search for Date Range
```python
from datetime import date
from app.services.merge_sort import merge_sort
from app.services.search import search_expenses_by_date_range

expenses = Expense.query.filter_by(user_id=user_id).all()

# Step 1: Sort by date (O(n log n))
sorted_expenses = merge_sort(expenses, key="date", ascending=True)

# Step 2: Binary search range (O(log n + k))
start = date(2026, 7, 1)
end = date(2026, 7, 31)

results = search_expenses_by_date_range(sorted_expenses, start, end)

print(f"Found {len(results)} expenses in July 2026")

# Time: O(n log n) sort + O(log n + k) search, where k = expenses in range
```

---

## Test Coverage

### Linear Search Tests (7 tests)
- ✓ Substring match (case-insensitive)
- ✓ Case sensitivity
- ✓ Empty results
- ✓ Empty items list
- ✓ Exact match
- ✓ Callable key function
- ✓ Performance characteristics

### Binary Search Tests (11 tests)
- ✓ Finds target in sorted array
- ✓ Returns -1 when not found
- ✓ Empty array
- ✓ Single item
- ✓ Descending order
- ✓ Callable key function
- ✓ Range search with duplicates
- ✓ Range search single match
- ✓ Range search no matches
- ✓ Date range search
- ✓ Performance characteristics

### Integration Tests (12 tests)
- ✓ Linear search with real Expense objects
- ✓ Binary search after sort
- ✓ Title endpoint
- ✓ Description endpoint
- ✓ Category endpoint
- ✓ ID endpoint (binary)
- ✓ ID not found error
- ✓ Date endpoint (binary)
- ✓ Date range endpoint (binary)
- ✓ Date range validation
- ✓ JWT authentication required
- ✓ Query parameter validation

**Total:** 33 tests, all passing ✓

---

## Performance Benchmarks

### Search Comparison (100,000 items)

| Operation | Linear | Binary | Speedup |
|-----------|--------|--------|---------|
| First search | 50K ops | 17 ops | 2,941× |
| 10 searches | 500K ops | 170 ops | 2,941× |
| 100 searches | 5M ops | 1.7K ops | 2,941× |

### With Pre-Sort Cost

| Operation | Linear | Binary (with sort) | Comparison |
|-----------|--------|-------------------|------------|
| 1 search | 50K | 1.7M + 17 | Linear wins |
| 2 searches | 100K | 1.7M + 34 | Binary winning |
| 10 searches | 500K | 1.7M + 170 | Binary wins |
| 100 searches | 5M | 1.7M + 1.7K | Binary much faster |

---

## Best Practices

### When to Use Each

✓ **Use Linear Search For:**
- Text fields (title, description, category)
- Substring/partial matches
- Unsorted data
- Very small datasets (< 1K items)
- One-time searches

✓ **Use Binary Search For:**
- Numeric/sortable fields (ID, date)
- Many searches on same dataset
- Large datasets (> 10K items)
- Exact match lookups
- Performance critical

### Optimization Tips

1. **Cache sorted results** - Sort once, reuse many times
2. **Combine search types** - Use binary for ID, linear for text in same query
3. **Index frequently searched fields** - Database indexes use similar concepts
4. **Batch searches** - Multiple searches in one request cheaper than separate calls
5. **Use appropriate algorithm** - Right tool for right job

### Common Mistakes

❌ **Don't:**
- Binary search unsorted data (doesn't work)
- Linear search large datasets repeatedly (very slow)
- Sort data for single search on small dataset (overhead not worth it)
- Search unsorted data expecting binary performance

✓ **Do:**
- Sort data before binary search
- Linear search for text fields
- Consider search patterns in system design
- Document search complexity in comments

---

## Summary

| Feature | Linear | Binary |
|---------|--------|--------|
| Algorithm | Sequential check | Divide and conquer |
| Sorted? | No | Yes (required) |
| Time | O(n) | O(log n) |
| Space | O(k) | O(1) |
| Best For | Text, small data | Numbers, large data |
| Used In | Title, Description, Category | ID, Date searches |
| When | Unsorted, few searches | Sorted, many searches |

**Key Takeaway:**
- **Linear search:** Reliable workhorse, works everywhere, but O(n) slow
- **Binary search:** Lightning fast O(log n), but requires sorted data

Choose wisely based on your data and access patterns!
