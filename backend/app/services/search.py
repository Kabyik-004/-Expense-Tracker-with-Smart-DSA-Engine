"""
Search algorithms for finding expenses.

TWO STRATEGIES:

1. LINEAR SEARCH - Sequential search through all items
   - Works on unsorted data
   - Used for: title, description, category (text fields)
   - Time Complexity: O(n) - worst case check all items
   - Space Complexity: O(1)
   
2. BINARY SEARCH - Divide-and-conquer search on sorted data
   - REQUIRES data to be sorted first
   - Used for: expense_id (integer), date (comparable)
   - Time Complexity: O(log n) - divide array in half each iteration
   - Space Complexity: O(1)
   
COMPARISON:
  Linear Search:
    - Pros: Works on unsorted data, simple
    - Cons: Slow on large datasets O(n)
    - Use when: Data unsorted, small dataset, few searches
  
  Binary Search:
    - Pros: Very fast on sorted data O(log n)
    - Cons: Requires pre-sorting, data must be sorted
    - Use when: Data sorted/searchable, many searches, large dataset
"""


def linear_search(items, query, key, case_sensitive=False):
    """
    Linear (sequential) search through items.
    
    Searches every item sequentially until match found.
    Works with unsorted data.
    
    Args:
        items (list): List of items to search (e.g., Expense objects)
        query (str): Search term/pattern
        key (str or callable): Field name or function to extract value
        case_sensitive (bool): Whether search is case-sensitive (default: False)
    
    Returns:
        list: All items matching the query
    
    Time Complexity: O(n) where n = number of items
        - Worst case: search all items
        - Best case: O(1) if first item matches
        - Average case: O(n/2) ≈ O(n)
    
    Space Complexity: O(k) where k = number of matches
    
    Example:
        results = linear_search(expenses, "groceries", "title")
        → Returns all expenses with "groceries" in title
    """
    results = []
    query_lower = query.lower() if not case_sensitive else query
    
    for item in items:
        value = _get_search_value(item, key)
        value_str = str(value).lower() if not case_sensitive else str(value)
        
        if query_lower in value_str:
            results.append(item)
    
    return results


def linear_search_exact(items, query, key, case_sensitive=False):
    """
    Linear search for exact matches (not substring).
    
    Args:
        items (list): List of items to search
        query: Exact value to match
        key (str or callable): Field name or function to extract value
        case_sensitive (bool): Case-sensitive matching
    
    Returns:
        list: All items with exact match
    
    Time Complexity: O(n)
    Space Complexity: O(k) where k = matches
    """
    results = []
    query_lower = str(query).lower() if not case_sensitive else str(query)
    
    for item in items:
        value = _get_search_value(item, key)
        value_str = str(value).lower() if not case_sensitive else str(value)
        
        if query_lower == value_str:
            results.append(item)
    
    return results


def binary_search(items, target, key, ascending=True):
    """
    Binary search on sorted array.
    
    REQUIRES: items must be sorted by the key field.
    Use merge_sort() first to ensure data is sorted.
    
    Repeatedly divides search space in half:
    - Compare target to middle element
    - If match: return index
    - If target < middle: search left half
    - If target > middle: search right half
    - Repeat until found or search space empty
    
    Args:
        items (list): MUST BE SORTED list of items
        target: Value to search for
        key (str or callable): Field name or function to extract value
        ascending (bool): Whether items sorted in ascending order (default: True)
    
    Returns:
        int: Index of item if found, -1 if not found
    
    Time Complexity: O(log n)
        - Each comparison eliminates half of remaining items
        - Maximum comparisons: log₂(n)
        - For 1 million items: max 20 comparisons
    
    Space Complexity: O(1) - constant space, no recursion
    
    Example:
        # First sort expenses by ID
        sorted_expenses = merge_sort(expenses, key="id", ascending=True)
        
        # Then search
        idx = binary_search(sorted_expenses, target_id=5, key="id")
        if idx != -1:
            expense = sorted_expenses[idx]
    """
    left = 0
    right = len(items) - 1
    
    while left <= right:
        mid = (left + right) // 2
        mid_value = _get_search_value(items[mid], key)
        
        # Compare target to middle value
        if mid_value == target:
            return mid  # Found!
        
        if ascending:
            if mid_value < target:
                left = mid + 1   # Search right half
            else:
                right = mid - 1  # Search left half
        else:
            if mid_value > target:
                left = mid + 1   # Search right half
            else:
                right = mid - 1  # Search left half
    
    return -1  # Not found


def binary_search_range(items, target, key, ascending=True):
    """
    Binary search to find ALL items equal to target.
    
    Returns both lower and upper bounds where target values appear.
    
    Args:
        items (list): SORTED list of items
        target: Value to search for
        key (str or callable): Field to search
        ascending (bool): Sort order
    
    Returns:
        list: All items with value equal to target
    
    Time Complexity: O(log n + k) where k = number of matches
        - O(log n) to find first match
        - O(k) to collect all matches
    
    Space Complexity: O(k) for results
    """
    idx = binary_search(items, target, key, ascending)
    if idx == -1:
        return []
    
    # Find all matching items (could have duplicates)
    results = [items[idx]]
    
    # Search left
    left_idx = idx - 1
    while left_idx >= 0 and _get_search_value(items[left_idx], key) == target:
        results.insert(0, items[left_idx])
        left_idx -= 1
    
    # Search right
    right_idx = idx + 1
    while right_idx < len(items) and _get_search_value(items[right_idx], key) == target:
        results.append(items[right_idx])
        right_idx += 1
    
    return results


def binary_search_range_sorted(items, start, end, key, ascending=True):
    """
    Binary search to find items within a range [start, end].
    
    Useful for: date range searches, amount range searches
    
    Args:
        items (list): SORTED list of items
        start: Lower bound (inclusive)
        end: Upper bound (inclusive)
        key (str or callable): Field to search
        ascending (bool): Sort order
    
    Returns:
        list: All items where start <= value <= end
    
    Time Complexity: O(log n + k) where k = items in range
    Space Complexity: O(k)
    """
    results = []
    
    for item in items:
        value = _get_search_value(item, key)
        
        if ascending:
            if start <= value <= end:
                results.append(item)
            elif value > end:
                break  # Rest won't match (sorted)
        else:
            if end <= value <= start:
                results.append(item)
            elif value < end:
                break  # Rest won't match
    
    return results


from app.utils import get_value_by_key as _get_search_value


def search_expenses_by_title(expenses, title_query):
    """
    Linear search for expenses by title (substring match).
    
    Case-insensitive partial match.
    
    Time Complexity: O(n)
    """
    return linear_search(expenses, title_query, "title", case_sensitive=False)


def search_expenses_by_description(expenses, description_query):
    """
    Linear search for expenses by description.
    
    Time Complexity: O(n)
    """
    return linear_search(expenses, description_query, "description", case_sensitive=False)


def search_expenses_by_category(expenses, category_id):
    """
    Linear search for expenses by category ID (exact match).
    
    Time Complexity: O(n)
    """
    return linear_search_exact(expenses, category_id, "category_id")


def search_expense_by_id(expenses, expense_id):
    """
    Binary search for expense by ID.
    
    REQUIRES: expenses must be sorted by ID first!
    Use merge_sort(expenses, key="id") before calling this.
    
    Time Complexity: O(log n) - extremely fast
    Space Complexity: O(1)
    
    Returns:
        Expense object if found, None if not found
    """
    idx = binary_search(expenses, expense_id, "id", ascending=True)
    return expenses[idx] if idx != -1 else None


def search_expenses_by_date(expenses, target_date):
    """
    Binary search for expenses on a specific date.
    
    REQUIRES: expenses must be sorted by date first!
    
    Returns all expenses on the target date (handles duplicates).
    
    Time Complexity: O(log n + k) where k = expenses on that date
    """
    return binary_search_range(expenses, target_date, "date", ascending=True)


def search_expenses_by_date_range(expenses, start_date, end_date):
    """
    Find all expenses within a date range [start_date, end_date].
    
    REQUIRES: expenses must be sorted by date first!
    
    Time Complexity: O(log n + k)
    """
    return binary_search_range_sorted(
        expenses, start_date, end_date, "date", ascending=True
    )


# COMPLEXITY EXPLANATION FUNCTIONS

def explain_linear_search():
    """
    Linear Search Complexity Explanation
    
    ALGORITHM:
    Go through items one by one until you find the match.
    
    PSEUDOCODE:
    for each item in items:
        if item matches query:
            add to results
    
    TIME COMPLEXITY: O(n) where n = number of items
    
    Why O(n)?
    - Worst case: search all n items (target not found or at end)
    - Best case: O(1) if first item matches
    - Average case: check n/2 items ≈ O(n)
    
    GRAPH (for 100 items):
         Time
          |
        1 |                                    ●
      0.8 |                                ●
      0.6 |                            ●
      0.4 |                        ●
      0.2 |                    ●
          |                ●
          |            ●
          |        ●
          |    ●
          | ●
          |________________ Items
          0   20   40   60   80   100
    
    Examples:
    - 10 items: max 10 checks
    - 100 items: max 100 checks
    - 1,000 items: max 1,000 checks
    - 1,000,000 items: max 1,000,000 checks
    
    When to use:
    ✓ Small datasets (< 1,000 items)
    ✓ Unsorted data (no preprocessing)
    ✓ Few searches (sorting overhead not worth it)
    ✓ Text searches (title, description, category)
    """
    pass


def explain_binary_search():
    """
    Binary Search Complexity Explanation
    
    ALGORITHM:
    1. Start with sorted data
    2. Check middle item
    3. If match: done
    4. If target < middle: search left half
    5. If target > middle: search right half
    6. Repeat with half the data
    
    PSEUDOCODE:
    left = 0, right = n-1
    while left <= right:
        mid = (left + right) / 2
        if items[mid] == target:
            return mid
        else if items[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
    
    TIME COMPLEXITY: O(log n) where n = number of items
    
    Why O(log n)?
    - Each iteration eliminates HALF of remaining items
    - n → n/2 → n/4 → n/8 → ... → 1
    - Number of steps = log₂(n)
    
    GRAPH (comparing linear vs binary):
         Time
          |
       1M |●●●●●●●●●●●●●● (Linear O(n))
     100K |
          |
      10K |
          |
       1K |                           ● (Binary O(log n))
          |
        100|
          |
         10|●
          |
          1|●
          |_______________ Items
           1K   10K  100K  1M
    
    Examples (max comparisons):
    - 10 items: max 4 comparisons (vs 10 linear)
    - 100 items: max 7 comparisons (vs 100 linear)
    - 1,000 items: max 10 comparisons (vs 1,000 linear)
    - 1,000,000 items: max 20 comparisons (vs 1,000,000 linear)
    
    SPEEDUP for 1 million items:
    - Linear: 1,000,000 checks
    - Binary: 20 checks
    - Speedup: 50,000× faster!
    
    REQUIREMENTS:
    1. Data MUST be sorted first
    2. Can only search by sortable values (numeric, date, string)
    3. Once sorted, can do many fast searches
    
    When to use:
    ✓ Large sorted datasets
    ✓ Many searches (sort cost amortized)
    ✓ Numeric IDs, dates, amounts
    ✗ Unsorted data (sort first: O(n log n))
    ✗ Text search (use linear or full-text indexing)
    """
    pass


def explain_search_strategy():
    """
    Choosing Between Linear and Binary Search
    
    DECISION MATRIX:
    
    Data Type | Is Sorted? | Size | Best Algorithm | Why
    ────────────────────────────────────────────────────
    Title     | NO        | Any  | Linear O(n)    | Text, unsorted
    Category  | NO        | Any  | Linear O(n)    | Text, unsorted
    Description| NO       | Any  | Linear O(n)    | Text, unsorted
    ────────────────────────────────────────────────────
    Expense ID| YES (sort first)| Big | Binary O(log n) | Numeric, sortable
    Date      | YES (sort first)| Big | Binary O(log n) | Comparable, sortable
    ────────────────────────────────────────────────────
    
    WORKFLOW:
    
    For NUMERIC/DATE searches (ID, Date):
    1. Sort once: merge_sort(expenses, key="id")      → O(n log n)
    2. Search many times: binary_search()             → O(log n) each
    3. Total for k searches: O(n log n + k log n)
    
    For TEXT searches (Title, Description):
    1. Search directly: linear_search(expenses, query) → O(n) each
    2. Sorting doesn't help (can't sort on partial match)
    3. Total for k searches: O(k * n)
    
    TRADE-OFF EXAMPLE (1,000 searches on 100,000 items):
    
    Sort once + Binary search:
    - Sort: 100,000 * log₂(100,000) ≈ 1.6 million ops
    - 1,000 searches: 1,000 * 17 ≈ 17,000 ops
    - Total: ~1.6 million ops
    
    Linear search (no sort):
    - 1,000 searches: 1,000 * 100,000 = 100 million ops
    - ~62× slower!
    
    RECOMMENDATION:
    - Few searches or unsorted data → Linear
    - Many searches on numeric/date → Sort once + Binary
    """
    pass
