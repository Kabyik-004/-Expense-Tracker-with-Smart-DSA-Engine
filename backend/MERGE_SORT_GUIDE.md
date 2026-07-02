## Merge Sort Implementation & Documentation

### Overview

**Merge Sort** is a divide-and-conquer sorting algorithm that recursively divides an array in half, sorts each half, and merges them back together in sorted order.

---

## 1. ALGORITHM EXPLANATION

### How It Works

```
Divide Phase:
  [38, 27, 43, 3]
       ↓
  [38, 27]  [43, 3]
     ↓        ↓
  [38][27]  [43][3]    ← Base case: single elements

Merge Phase:
  [27, 38]  [3, 43]
       ↓
  [3, 27, 38, 43]      ← Sorted result
```

### Pseudocode

```
merge_sort(array, left, right):
    if left >= right:
        return  # Base case: single element is sorted
    
    mid = (left + right) / 2
    
    # Divide
    merge_sort(array, left, mid)      # Sort left half
    merge_sort(array, mid+1, right)   # Sort right half
    
    # Conquer
    merge(array, left, mid, right)    # Merge sorted halves
```

---

## 2. RECURSION EXPLANATION

### What is Recursion?

**Recursion** is when a function calls itself to solve smaller subproblems of the same type.

### Recursion in Merge Sort

```python
def merge_sort(items, key, ascending, left=0, right=None):
    if right is None:
        right = len(items) - 1
    
    # BASE CASE: Stop recursion when array has ≤1 element
    if left >= right:
        return items[left : right + 1]
    
    # RECURSIVE CASE: Divide and conquer
    mid = (left + right) // 2
    
    merge_sort(items, key, ascending, left, mid)      # ← Recursive call 1
    merge_sort(items, key, ascending, mid + 1, right) # ← Recursive call 2
    
    _merge(items, key, ascending, left, mid, right)
    return items
```

### Call Stack Visualization (for [38, 27, 43, 3])

```
CALL STACK (showing depth):

Level 1: merge_sort([38, 27, 43, 3], left=0, right=3)
  │
  ├─ Level 2: merge_sort([38, 27], left=0, right=1)
  │   │
  │   ├─ Level 3: merge_sort([38], left=0, right=0)
  │   │   → BASE CASE: return [38]
  │   │
  │   └─ Level 3: merge_sort([27], left=1, right=1)
  │       → BASE CASE: return [27]
  │   
  │   → MERGE: [38] + [27] = [27, 38]
  │
  └─ Level 2: merge_sort([43, 3], left=2, right=3)
      │
      ├─ Level 3: merge_sort([43], left=2, right=2)
      │   → BASE CASE: return [43]
      │
      └─ Level 3: merge_sort([3], left=3, right=3)
          → BASE CASE: return [3]
      
      → MERGE: [43] + [3] = [3, 43]

→ FINAL MERGE: [27, 38] + [3, 43] = [3, 27, 38, 43]
```

### Key Recursion Properties

1. **Base Case**: Single element arrays are already sorted
2. **Recursive Step**: Split problem into smaller subproblems
3. **Call Depth**: Maximum stack depth = O(log n)
4. **Combining**: Merge step combines sorted results

---

## 3. COMPLEXITY ANALYSIS

### Time Complexity: **O(n log n)** - ALL CASES

```
T(n) = 2 × T(n/2) + O(n)
       ↑             ↑
    Two recursive  Merge step
    calls on half  takes O(n)
    the array

Solving this recurrence:
- Depth of recursion tree: log₂(n) levels
- Work at each level: O(n)
- Total: O(n) × O(log n) = O(n log n)
```

#### Breakdown

| Case | Time | Reason |
|------|------|--------|
| **Best** | O(n log n) | Already sorted (still divides/merges) |
| **Average** | O(n log n) | Random order |
| **Worst** | O(n log n) | Reverse sorted |

**Key Insight**: Merge sort **guarantees** O(n log n) regardless of input!

### Space Complexity: **O(n)**

```
Auxiliary space needed:
- Temporary arrays during merge: O(n)
- Recursion call stack: O(log n)
- Total: O(n)

Unlike quicksort (O(1) space), merge sort requires
extra memory for temporary subarrays during merging.
```

### Comparison with Other Algorithms

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | ✓ |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | ✗ |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | ✗ |
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | ✓ |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | ✓ |

---

## 4. IMPLEMENTATION FEATURES

### Sorting by Field

```python
# Sort by single field
sort_expenses(expenses, sort_by="amount", ascending=False)

Supported fields:
- "amount"       : Sort by expense amount
- "date"         : Sort by expense date
- "category_id"  : Sort by category
- "title"        : Sort by expense title
```

### Sorting by Multiple Fields (Stable Sort)

```python
# Sort expenses: by category (ascending), then amount (descending)
sort_expenses_multi(
    expenses,
    sort_fields=["category_id", "amount"],
    ascending_list=[True, False]
)

Result: Category 1 with highest amounts first, then Category 2, etc.
```

### Stable Sort Property

Merge sort is **stable**: equal elements maintain their relative order.

```python
expenses = [
    {"id": 1, "amount": 100},
    {"id": 2, "amount": 50},
    {"id": 3, "amount": 100},  ← Same amount as id=1
]

After sorting by amount (ascending):
[
    {"id": 2, "amount": 50},
    {"id": 1, "amount": 100},  ← Maintains order (1 before 3)
    {"id": 3, "amount": 100},
]
```

---

## 5. API ENDPOINTS

### Single Field Sort

**GET** `/api/expenses/sort/single`

Query Parameters:
- `sort_by`: "amount" | "date" | "category_id" | "title" (default: "amount")
- `ascending`: "true" | "false" (default: "true")

Example:
```bash
GET /api/expenses/sort/single?sort_by=amount&ascending=false
```

Response:
```json
{
  "success": true,
  "data": {
    "expenses": [
      { "id": 1, "title": "Dinner", "amount": 50.0, "date": "2026-07-01", ... },
      { "id": 2, "title": "Lunch", "amount": 30.0, "date": "2026-07-02", ... }
    ]
  },
  "message": "Expenses sorted by amount (descending)"
}
```

### Multi-Field Sort

**POST** `/api/expenses/sort/multi`

Request Body:
```json
{
  "sort_fields": ["category_id", "amount"],
  "ascending": [true, false]
}
```

Response: Same as single field sort

---

## 6. USAGE EXAMPLES

### Python Usage

```python
from app.services.merge_sort import sort_expenses, sort_expenses_multi

# Example 1: Sort by amount descending
sorted_exp = sort_expenses(expenses, sort_by="amount", ascending=False)

# Example 2: Sort by date ascending
sorted_exp = sort_expenses(expenses, sort_by="date", ascending=True)

# Example 3: Multi-field sort
sorted_exp = sort_expenses_multi(
    expenses,
    sort_fields=["category_id", "amount"],
    ascending_list=[True, False]  # Category asc, Amount desc
)
```

### HTTP Usage

```bash
# Sort by amount (descending)
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/api/expenses/sort/single?sort_by=amount&ascending=false"

# Sort by category, then amount (descending)
curl -X POST -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"sort_fields": ["category_id", "amount"], "ascending": [true, false]}' \
     http://localhost:5000/api/expenses/sort/multi
```

---

## 7. KEY ADVANTAGES

✓ **Guaranteed O(n log n)** - No worst-case degradation  
✓ **Stable sort** - Preserves relative order of equal elements  
✓ **Predictable** - Performance independent of input distribution  
✓ **External sort** - Works well with external storage (sequential I/O)  

---

## 8. KEY DISADVANTAGES

✗ **O(n) space** - Requires temporary arrays (vs. O(1) for quicksort)  
✗ **Slower on average** - More work than quicksort for random data  
✗ **Not in-place** - Extra memory overhead  

---

## 9. WHEN TO USE

**Merge Sort is ideal when:**
- You need guaranteed O(n log n) performance
- Stability is required
- Extra memory is available
- Working with linked lists
- External sorting is needed

**Use quicksort instead when:**
- In-place sorting is required
- Average-case performance matters more than worst-case
- Memory is extremely limited

---

## 10. TEST COVERAGE

All implementations are tested with:

**Unit Tests** (`test_merge_sort.py`):
- ✓ Basic ascending/descending sort
- ✓ Empty and single-element arrays
- ✓ Duplicate handling
- ✓ Already-sorted and reverse-sorted inputs
- ✓ Stability verification
- ✓ Multi-field sorting

**Integration Tests**:
- ✓ Single-field sort endpoints
- ✓ Multi-field sort endpoints
- ✓ Invalid field validation
- ✓ Empty expense lists

**Result**: 21/21 tests passing ✓

---

## 11. TECHNICAL NOTES

### Merge Operation (Core Merging Logic)

```python
def _merge(items, key, ascending, left, mid, right):
    """Merge two sorted subarrays in O(n) time."""
    
    # Create temporary arrays
    left_arr = items[left : mid + 1]      # [27, 38]
    right_arr = items[mid + 1 : right + 1]  # [3, 43]
    
    i = j = 0
    k = left
    
    # Compare and merge in sorted order
    while i < len(left_arr) and j < len(right_arr):
        left_val = left_arr[i]
        right_val = right_arr[j]
        
        # Choose smaller (or larger for descending)
        if (ascending and left_val <= right_val) or \
           (not ascending and left_val >= right_val):
            items[k] = left_arr[i]
            i += 1
        else:
            items[k] = right_arr[j]
            j += 1
        k += 1
    
    # Copy remaining elements
    while i < len(left_arr):
        items[k] = left_arr[i]
        i += 1
        k += 1
    
    while j < len(right_arr):
        items[k] = right_arr[j]
        j += 1
        k += 1
```

### Why Merge Takes O(n)?

Each element is visited exactly **once**:
- Moved from original array → temporary array: 1 visit
- Compared during merge: 1 visit
- Moved back to original array: 1 visit
- **Total**: 3n visits = O(n)

---

## 12. RECURSION TREE ANALYSIS

```
For n = 8 elements:

Level 0:     [8 elements]           Work: 8
             /            \
Level 1:  [4 ele]        [4 ele]    Work: 8
          /    \          /    \
Level 2: [2]  [2]        [2]  [2]   Work: 8
        / \   / \        / \   / \
Level 3: [1][1][1][1]    [1][1][1][1]  Work: 8 (base cases)

Levels: log₂(8) = 3
Work per level: 8 = n
Total work: 8 × 3 = 24 = n log n
```

---

## Summary

| Aspect | Value |
|--------|-------|
| **Algorithm** | Divide-and-Conquer |
| **Time Complexity** | O(n log n) guaranteed |
| **Space Complexity** | O(n) |
| **Stable** | Yes |
| **In-place** | No |
| **Best for** | Predictable performance, stability required |
| **Status** | Implemented & tested ✓ |
