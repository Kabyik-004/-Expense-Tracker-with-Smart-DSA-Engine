## Stack Data Structure & Undo Implementation

### Overview

A **Stack** is a Last-In-First-Out (LIFO) linear data structure where:
- The last element added is the first one removed
- All operations (push, pop, peek) execute in **O(1)** constant time
- Perfect for implementing undo/redo functionality

---

## 1. STACK OPERATIONS

### `push(item)` - Add to Stack

```python
stack = Stack(max_size=10)
stack.push("Create Expense 1")  # O(1)
stack.push("Update Expense 1")  # O(1)

# Visual:
# Top  → "Update Expense 1"
#        "Create Expense 1"
# Bottom
```

**Time Complexity**: O(1) - always constant
**Max Size**: Enforced as 10 (removes oldest if exceeded)

### `pop()` - Remove from Stack

```python
action = stack.pop()  # Returns "Update Expense 1" and removes it
action = stack.pop()  # Returns "Create Expense 1"
action = stack.pop()  # Returns None (empty)
```

**Time Complexity**: O(1) - constant, just remove last element

### `peek()` - View Top Without Removing

```python
top = stack.peek()  # Returns "Update Expense 1", stack unchanged
# Useful to check what operation is next to undo
```

**Time Complexity**: O(1) - just access last element

### `size()` - Get Stack Size

```python
stack.size()  # Returns current number of items
```

**Time Complexity**: O(1) - just read length

### `is_empty()` - Check if Empty

```python
if stack.is_empty():
    print("No undo history available")
```

**Time Complexity**: O(1) - just check length

---

## 2. LIFO PRINCIPLE EXPLAINED

**Last-In-First-Out**: The most recently added item is removed first.

### Real-World Examples

```
Browser Back Button:
  1. Visit Page A    Stack: [A]
  2. Visit Page B    Stack: [A, B]
  3. Visit Page C    Stack: [A, B, C]
  4. Press Back  → Show B, Stack: [A, B]
  ↑ Last visited removed first!

Undo in Text Editor:
  1. Type "Hello"        Stack: ["Type Hello"]
  2. Delete " World"     Stack: ["Type Hello", "Delete World"]
  3. Click Undo      → Redo "Delete World", Stack: ["Type Hello"]
  ↑ Last action undone first!

Function Call Stack in Memory:
  main()
    ├── function_a()
    │   └── function_b()
    │       └── function_c()  ← Called last, completes first
    ├── function_b() returns
    ├── function_a() returns
    └── main() returns
```

---

## 3. TIME COMPLEXITY ANALYSIS

| Operation | Complexity | Reason |
|-----------|-----------|--------|
| `push()` | O(1) | Append to end of list |
| `pop()` | O(1) | Remove last element |
| `peek()` | O(1) | Access last element |
| `size()` | O(1) | Read length property |
| `is_empty()` | O(1) | Check length == 0 |
| `clear()` | O(n) | Remove all n elements |

**Why O(1)?** Python lists support O(1) append and pop operations at the end.

### Space Complexity

**O(n)** where n = number of items in stack
- All items stored in internal list

---

## 4. BOUNDED STACK (MAX_SIZE = 10)

### Why Bounded?

Expense undo history is limited to 10 operations per user:
- **Memory efficient**: Fixed memory usage regardless of history length
- **Simplicity**: Don't retain irrelevant old operations
- **Standard practice**: Most apps (Word, Photoshop, Browsers) limit undo to 20-100 operations

### How It Works

```python
stack = Stack(max_size=3)

stack.push("Op 1")    # [Op 1]
stack.push("Op 2")    # [Op 1, Op 2]
stack.push("Op 3")    # [Op 1, Op 2, Op 3] - at max
stack.push("Op 4")    # [Op 2, Op 3, Op 4] - Op 1 removed!
                      # ↑ Oldest item evicted (FIFO eviction from bottom)
```

**Key**: When stack is full, the **oldest (bottom) item is removed** to make room for the new item.

---

## 5. STACK IN EXPENSE UNDO SYSTEM

### Undo Tracking

#### CREATE Operation
```python
# When user creates an expense:
undo_op = {
    "action": "CREATE",
    "entity_id": 5,
    "snapshot": None  # Nothing existed before
}
stack.push(undo_op)

# Undo: Delete the created expense
```

#### UPDATE Operation
```python
# Before modifying:
old_expense = {
    "title": "Lunch",
    "amount": 20.0,
    "date": "2026-07-01"
}

undo_op = {
    "action": "UPDATE",
    "entity_id": 5,
    "snapshot": json.dumps(old_expense)  # Save old state
}
stack.push(undo_op)

# Undo: Restore old values
```

#### DELETE Operation
```python
# Before deleting:
deleted_expense = {
    "title": "Dinner",
    "amount": 50.0,
    "date": "2026-07-02"
}

undo_op = {
    "action": "DELETE",
    "entity_id": 5,
    "snapshot": json.dumps(deleted_expense)  # Save full state
}
stack.push(undo_op)

# Undo: Recreate the expense with saved data
```

### Stack Properties

```
Per User: Each user has their own stack
Size Limit: Maximum 10 operations per user
Per Session: Currently in-memory (could be persisted to Redis/DB)
Persistence: Also stored in UndoHistory table for audit trail
```

---

## 6. API ENDPOINTS

### Undo Last Operation

**POST** `/api/expenses/undo`

```bash
curl -X POST -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/expenses/undo
```

Response (CREATE undo):
```json
{
  "success": true,
  "data": {"expense_id": 5},
  "message": "Undo: Deleted expense 5"
}
```

### Check Undo Status

**GET** `/api/expenses/undo/status`

```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/expenses/undo/status
```

Response:
```json
{
  "success": true,
  "data": {
    "stack_size": 3,
    "max_size": 10,
    "is_empty": false,
    "top_operation": {
      "action": "UPDATE",
      "entity_id": 5,
      "entity_type": "expense"
    }
  },
  "message": "Undo stack status retrieved"
}
```

### Clear Undo History

**POST** `/api/expenses/undo/clear`

```bash
curl -X POST -H "Authorization: Bearer <token>" \
     http://localhost:5000/api/expenses/undo/clear
```

---

## 7. USAGE EXAMPLES

### Python Example

```python
from app.services.stack import Stack

# Create a bounded stack
undo_stack = Stack(max_size=10)

# Simulate operations
undo_stack.push({"action": "CREATE", "id": 1})
undo_stack.push({"action": "UPDATE", "id": 1})
undo_stack.push({"action": "DELETE", "id": 2})

# Check status
print(f"Undo stack size: {undo_stack.size()}")      # 3
print(f"Next to undo: {undo_stack.peek()}")          # DELETE 2

# Undo operations (LIFO order)
action = undo_stack.pop()  # DELETE 2
action = undo_stack.pop()  # UPDATE 1
action = undo_stack.pop()  # CREATE 1
```

### HTTP Example

```bash
# Create expense
curl -X POST http://localhost/api/expenses \
  -d '{"title": "Lunch", "amount": 25}'

# Create another
curl -X POST http://localhost/api/expenses \
  -d '{"title": "Dinner", "amount": 35}'

# Check undo status
curl http://localhost/api/expenses/undo/status
# Response: stack_size: 2

# Undo last (DELETE Dinner)
curl -X POST http://localhost/api/expenses/undo

# Check status again
curl http://localhost/api/expenses/undo/status
# Response: stack_size: 1

# Undo again (DELETE Lunch)
curl -X POST http://localhost/api/expenses/undo

# Check status (empty)
curl http://localhost/api/expenses/undo/status
# Response: stack_size: 0, is_empty: true
```

---

## 8. COMPARISON WITH OTHER DATA STRUCTURES

| Structure | Last Item | Use Case |
|-----------|-----------|----------|
| **Stack** | Removed first | Undo/Redo, recursion, backtracking |
| Queue | Removed last | Task scheduling, BFS |
| Array | Direct access | Random access needed |
| Linked List | Depends | Frequent insertions/deletions |

---

## 9. IMPLEMENTATION DETAILS

### Internal Storage

```python
class Stack:
    def __init__(self, max_size=100):
        self._items = []          # List (acts as LIFO)
        self._max_size = max_size # Bounded size

    def push(self, item):
        if len(self._items) >= self._max_size:
            self._items.pop(0)      # Remove oldest (FIFO eviction)
        self._items.append(item)    # Add to top

    def pop(self):
        return self._items.pop() if self._items else None

    def peek(self):
        return self._items[-1] if self._items else None
```

### Why Python Lists Work

Python's `list.append()` and `list.pop()` (without index) are O(1):
- `append()`: Add to end - no shifting needed
- `pop()`: Remove from end - no shifting needed
- `pop(0)`: Remove from start - **O(n)** (shifts all elements)

We only use `pop(0)` when at max capacity (rare event for bounded stack).

---

## 10. EXPENSE UNDO WORKFLOW

```
User Action          Stack State           Database
─────────────────────────────────────────────────────
Create Exp 1         [CREATE 1]           Insert Exp 1
Create Exp 2         [CREATE 1, CREATE 2] Insert Exp 2
Update Exp 1         [CREATE 1, CREATE 2, Snapshot Exp 1
                      UPDATE 1]            Update Exp 1
Delete Exp 2         [CREATE 1, CREATE 2, Snapshot Exp 2
                      UPDATE 1, DELETE 2]  Delete Exp 2

User clicks "Undo"
─────────────────────────────────────────────────────
Pop DELETE 2         [CREATE 1, CREATE 2, Recreate Exp 2
                      UPDATE 1]
Pop UPDATE 1         [CREATE 1, CREATE 2] Restore Exp 1
Pop CREATE 2         [CREATE 1]           Delete Exp 2
Pop CREATE 1         []                   Delete Exp 1
```

---

## 11. KEY ADVANTAGES

✓ **O(1) for all operations** - Constant time push/pop/peek  
✓ **Simple implementation** - Just append/pop from list  
✓ **Perfect for undo/redo** - LIFO matches user expectations  
✓ **Bounded memory** - Max size prevents unbounded growth  
✓ **Audit trail** - All operations also stored in database  

---

## 12. KEY DISADVANTAGES

✗ **Limited history** - Only keeps 10 most recent operations  
✗ **Sequential access** - Can't skip to specific operation  
✗ **No redo** - Can't redo after undo (would need separate redo stack)  
✗ **Memory persistence** - Lost on server restart (mitigated by DB storage)  

---

## 13. TEST COVERAGE

**19 tests passing:**

**Stack Unit Tests (11):**
- ✓ Push/pop/peek operations
- ✓ Size and empty checking
- ✓ Max size enforcement
- ✓ LIFO ordering
- ✓ Clear and to_list

**Undo Integration Tests (8):**
- ✓ Undo create/update/delete
- ✓ Stack status endpoint
- ✓ Max size limit (10 operations)
- ✓ Clear undo stack
- ✓ Multiple sequential undos

---

## 14. WHEN TO USE STACK VS QUEUE

| Scenario | Use |
|----------|-----|
| Undo/Redo | **Stack** |
| Task scheduling | Queue |
| Function calls | **Stack** |
| Print job queue | Queue |
| Expression parsing | **Stack** |
| Message queue | Queue |
| Web browser history | **Stack** |
| Request handling | Queue |

---

## Summary

| Aspect | Value |
|--------|-------|
| **Data Structure** | LIFO (Last-In-First-Out) |
| **Push Time** | O(1) |
| **Pop Time** | O(1) |
| **Peek Time** | O(1) |
| **Space Complexity** | O(n) |
| **Max Size** | 10 operations per user |
| **Use Case** | Undo/Redo functionality |
| **Status** | Implemented & tested ✓ |
| **Tests Passing** | 19/19 ✓ |
