"""
Merge Sort implementation for sorting expenses.

MERGE SORT EXPLANATION:
  A divide-and-conquer algorithm that:
  1. DIVIDES the array recursively into halves until reaching single elements
  2. MERGES the sorted halves back together while comparing and ordering elements
  
  Recursion Flow:
  - Base case: arrays with 1 element are already sorted
  - Recursive case: split array at midpoint, recursively sort each half,
    then merge the sorted halves in O(n) time

TIME COMPLEXITY: O(n log n) - all cases (best, average, worst)
  - Divide phase: O(log n) - tree depth
  - Merge phase: O(n) - at each level
  - Total: O(log n) × O(n) = O(n log n)

SPACE COMPLEXITY: O(n) - temporary arrays during merge

ADVANTAGES:
  - Stable sort (maintains relative order of equal elements)
  - Guaranteed O(n log n) performance
  - Predictable behavior
  
DISADVANTAGES:
  - Requires extra O(n) space
  - Slower than quicksort on average for random data
  - Not in-place
"""


def merge_sort(
    items,
    key="amount",
    ascending=True,
    left=0,
    right=None,
):
    """
    Sort items using merge sort algorithm.
    
    Args:
        items (list): List of expense objects or comparable items
        key (str or callable): Field name (for objects) or callable for comparison
        ascending (bool): Sort in ascending order if True, descending if False
        left (int): Start index (internal recursion parameter)
        right (int): End index (internal recursion parameter)
    
    Returns:
        list: Sorted copy of items
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    if right is None:
        right = len(items) - 1

    # BASE CASE: Single element or empty is already sorted
    if left >= right:
        return items[left : right + 1]

    # DIVIDE: Find midpoint and recursively sort both halves
    mid = (left + right) // 2

    # Recursively sort left half
    merge_sort(items, key=key, ascending=ascending, left=left, right=mid)

    # Recursively sort right half
    merge_sort(items, key=key, ascending=ascending, left=mid + 1, right=right)

    # CONQUER: Merge the two sorted halves
    _merge(items, key, ascending, left, mid, right)

    return items


def _merge(items, key, ascending, left, mid, right):
    """
    Merge two sorted subarrays: items[left:mid+1] and items[mid+1:right+1]
    
    This is the combining phase where sorted subarrays are merged in O(n) time.
    
    Args:
        items (list): Original list being sorted (modified in-place during merge)
        key (str or callable): Comparison key
        ascending (bool): Sort direction
        left (int): Start of left subarray
        mid (int): End of left subarray
        right (int): End of right subarray
    
    Time Complexity: O(n) where n = right - left + 1
    """
    # Create temporary arrays for the two halves
    left_arr = items[left : mid + 1]
    right_arr = items[mid + 1 : right + 1]

    i = j = 0  # Pointers for left and right arrays
    k = left  # Pointer for original array

    # Compare elements from both halves and merge in sorted order
    while i < len(left_arr) and j < len(right_arr):
        left_val = _get_sort_value(left_arr[i], key)
        right_val = _get_sort_value(right_arr[j], key)

        # Determine comparison: ascending or descending
        should_take_left = (
            (left_val <= right_val)
            if ascending
            else (left_val >= right_val)
        )

        if should_take_left:
            items[k] = left_arr[i]
            i += 1
        else:
            items[k] = right_arr[j]
            j += 1

        k += 1

    # Copy remaining elements from left array (if any)
    while i < len(left_arr):
        items[k] = left_arr[i]
        i += 1
        k += 1

    # Copy remaining elements from right array (if any)
    while j < len(right_arr):
        items[k] = right_arr[j]
        j += 1
        k += 1


from app.utils import get_value_by_key as _get_sort_value


def sort_expenses(expenses, sort_by="amount", ascending=True):
    """
    Sort expenses by a single field.
    
    Args:
        expenses (list): List of Expense objects
        sort_by (str): Field to sort by ("amount", "date", "category_id", "title")
        ascending (bool): Sort order
    
    Returns:
        list: Sorted list of expenses
    
    Example:
        sorted_exp = sort_expenses(expenses, sort_by="amount", ascending=False)
    """
    if not expenses:
        return []

    # Create a copy to avoid modifying original
    items_copy = expenses.copy()

    return merge_sort(items_copy, key=sort_by, ascending=ascending)


def sort_expenses_multi(expenses, sort_fields, ascending_list=None):
    """
    Sort expenses by multiple fields (stable sort).
    
    Sort by fields in reverse order of priority (last field = primary sort).
    Since merge sort is stable, sorting by field N then field M-1 then ... M gives
    results sorted by M, then M-1, etc. as tiebreaker.
    
    Args:
        expenses (list): List of Expense objects
        sort_fields (list): Fields to sort by, in order of priority
                           e.g., ["date", "amount"] sorts by amount, then date
        ascending_list (list): Booleans for each field (default: all True)
    
    Returns:
        list: Sorted list of expenses
    
    Example:
        # Sort by category (primary), then by amount descending (tiebreaker)
        sorted_exp = sort_expenses_multi(
            expenses,
            sort_fields=["category_id", "amount"],
            ascending_list=[True, False]
        )
    """
    if not expenses:
        return []

    if ascending_list is None:
        ascending_list = [True] * len(sort_fields)

    items_copy = expenses.copy()

    # Sort in reverse order of priority (last field becomes primary sort)
    for field, ascending in zip(reversed(sort_fields), reversed(ascending_list)):
        merge_sort(items_copy, key=field, ascending=ascending)

    return items_copy


# Recursion Explanation Example
def explain_recursion():
    """
    Explains merge sort recursion with a concrete example.
    
    Recursion in Merge Sort:
    
    1. DEFINITION: Recursion is a function calling itself to solve smaller
       subproblems of the same type.
    
    2. MERGE SORT RECURSION PATTERN:
       def merge_sort(array):
           if len(array) <= 1:  <-- BASE CASE (stops recursion)
               return array
           else:
               mid = len(array) // 2
               left = merge_sort(array[:mid])   <-- RECURSIVE CALL 1
               right = merge_sort(array[mid:])  <-- RECURSIVE CALL 2
               return merge(left, right)
    
    3. CALL STACK EXAMPLE for [38, 27, 43, 3]:
    
       Level 1: merge_sort([38, 27, 43, 3])
                     ├─ merge_sort([38, 27])         (LEFT)
                     │   ├─ merge_sort([38])          → returns [38]
                     │   └─ merge_sort([27])          → returns [27]
                     │   → merges to [27, 38]
                     │
                     └─ merge_sort([43, 3])          (RIGHT)
                         ├─ merge_sort([43])          → returns [43]
                         └─ merge_sort([3])           → returns [3]
                         → merges to [3, 43]
    
       Level 2: merge([27, 38], [3, 43]) → [3, 27, 38, 43]
    
    4. RECURSION PROPERTIES:
       - Depth: O(log n) levels
       - Each level processes O(n) total work
       - Total: O(n log n)
    
    5. STACK FRAMES:
       At deepest recursion: ~log n function calls on call stack
       Each frame stores: left, right, mid, and local variables
    """
    pass
