"""
Custom Stack implementation (LIFO - Last In, First Out).

A Stack is a linear data structure that operates on the Last-In-First-Out principle.
The most recently added element is the first one to be removed.

APPLICATIONS:
- Undo/Redo functionality
- Function call stack (recursion)
- Expression evaluation (postfix notation)
- Backtracking algorithms
- Browser back button

TIME COMPLEXITY:
- push(): O(1)
- pop(): O(1)
- peek(): O(1)
- size(): O(1)
- is_empty(): O(1)

SPACE COMPLEXITY: O(n) where n = number of elements

LIFO VISUALIZATION:
    push(4)    push(5)    pop()
    │ │        │ │        │ │
    └─┘        │ 5│       │ 5│  ← removed
    │ 4│       │ 4│       │ 4│
    └─┘        └─┘        └─┘
"""


from collections import deque


class Stack:
    """
    A generic LIFO (Last-In-First-Out) stack implementation.
    
    Features:
    - Fixed maximum size to prevent unbounded growth
    - All operations in O(1) constant time
    - Useful for undo/redo, expression evaluation, recursion simulation
    """

    def __init__(self, max_size=100):
        """
        Initialize an empty stack.
        
        Args:
            max_size (int): Maximum number of items the stack can hold.
                           Default: 100
        
        Time Complexity: O(1)
        """
        self._items = deque(maxlen=max_size)
        self._max_size = max_size

    def push(self, item):
        """
        Add an item to the top of the stack.

        If stack is at max capacity, the oldest (bottom) item is removed
        to maintain the size limit.

        Args:
            item: The item to add to the stack

        Returns:
            bool: True if item was added successfully

        Time Complexity: O(1)
        """
        self._items.append(item)
        return True

    def pop(self):
        """
        Remove and return the top item from the stack.
        
        Returns:
            The item at the top of the stack, or None if stack is empty
        
        Raises:
            IndexError: If stack is empty (optional behavior)
        
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.push("A")
            stack.push("B")
            item = stack.pop()  # Returns "B", stack is now ['A']
            item = stack.pop()  # Returns "A", stack is now []
            item = stack.pop()  # Returns None (or raises IndexError)
        """
        if len(self._items) == 0:
            return None
        return self._items.pop()

    def peek(self):
        """
        Return the top item without removing it.
        
        Returns:
            The item at the top of the stack, or None if stack is empty
        
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.push("A")
            stack.push("B")
            item = stack.peek()  # Returns "B", stack unchanged
            item = stack.peek()  # Still returns "B"
        """
        if len(self._items) == 0:
            return None
        return self._items[-1]

    def size(self):
        """
        Return the current number of items in the stack.
        
        Returns:
            int: Number of items in the stack
        
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.size()    # 0
            stack.push("A")
            stack.size()    # 1
            stack.push("B")
            stack.size()    # 2
            stack.pop()
            stack.size()    # 1
        """
        return len(self._items)

    def is_empty(self):
        """
        Check if the stack is empty.
        
        Returns:
            bool: True if stack has no items, False otherwise
        
        Time Complexity: O(1)
        
        Example:
            stack = Stack()
            stack.is_empty()  # True
            stack.push("A")
            stack.is_empty()  # False
            stack.pop()
            stack.is_empty()  # True
        """
        return len(self._items) == 0

    def is_full(self):
        """
        Check if the stack has reached maximum capacity.
        
        Returns:
            bool: True if stack size equals max_size
        
        Time Complexity: O(1)
        """
        return len(self._items) >= self._max_size

    def clear(self):
        """
        Remove all items from the stack.
        
        Time Complexity: O(n) where n = number of items
        """
        self._items.clear()

    def to_list(self):
        """
        Return a copy of the stack as a list (top at end).
        
        Returns:
            list: Copy of items in stack (bottom to top)
        
        Time Complexity: O(n)
        """
        return list(self._items)

    def __repr__(self):
        """String representation of the stack."""
        return f"Stack({self._items}, max_size={self._max_size})"

    def __len__(self):
        """Allow len(stack) to work."""
        return len(self._items)

    def __bool__(self):
        """Allow if stack: syntax to check if non-empty."""
        return len(self._items) > 0


# STACK USAGE EXAMPLES

def explain_lifo():
    """
    Explains LIFO (Last-In-First-Out) principle used by stacks.
    
    LIFO Definition:
    The element that is added last to the stack will be the first one to be removed.
    
    Real-world analogy:
    - Undo button: Last action is undone first
    - Browser back: Last visited page is shown first
    - Plate stack: Last plate put down is picked up first
    - Function calls: Last function called returns first
    
    Example Flow:
    
    Operations:     Stack State:        Explanation:
    push(1)         [1]                 1 is on top
    push(2)         [1, 2]              2 is now on top
    push(3)         [1, 2, 3]           3 is now on top
    pop()→3         [1, 2]              3 removed (last in, first out!)
    pop()→2         [1]                 2 removed
    pop()→1         []                  1 removed
    pop()→None      []                  Stack empty
    
    Key Properties:
    - Most recent additions are accessed first
    - Natural fit for undo/redo systems
    - Used in function call stacks in memory
    - Depth-first traversal of structures
    """
    pass


def explain_max_size_constraint():
    """
    Explains why maximum stack size is used in undo/redo systems.
    
    Problem Without Max Size:
    - Unlimited undo history consumes unbounded memory
    - Application grows slower over time
    - Old undo entries become irrelevant
    
    Solution: Bounded Stack (FIFO eviction at bottom)
    - Only keep last N actions
    - When full, discard oldest action
    - Memory usage stays constant
    
    Example with max_size=3:
    
    Operation           Stack State             Action
    push("Create 1")    ["Create 1"]
    push("Delete 1")    ["Create 1", "Delete 1"]
    push("Update 2")    ["Create 1", "Delete 1", "Update 2"]
    push("Create 2")    ["Delete 1", "Update 2", "Create 2"]
    ↑                   "Create 1" removed (oldest)
    
    When we try to undo:
    pop() → "Create 2"
    pop() → "Update 2"
    pop() → "Delete 1"
    pop() → None       (Can't undo "Create 1" anymore)
    
    Benefits of max_size=10:
    - Only 10 most recent actions remembered
    - Constant O(1) memory for undo system
    - Simple, predictable behavior
    - Common in real applications (Word, Photoshop, browsers)
    """
    pass
