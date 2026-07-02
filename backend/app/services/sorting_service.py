"""
Sorting Service
DSA algorithms: Merge Sort, Quick Sort, Heap Sort
Used for sorting expenses by amount, date, or category efficiently.
"""

import random
from app.utils import get_value_by_key


def quick_sort(items, key="amount", ascending=True):
    """Quick sort implementation (in-place, Hoare partition scheme)."""
    if len(items) <= 1:
        return items

    items_copy = items.copy()
    _quick_sort_recursive(items_copy, key, ascending, 0, len(items_copy) - 1)
    return items_copy


def _quick_sort_recursive(items, key, ascending, low, high):
    if low < high:
        pi = _partition(items, key, ascending, low, high)
        _quick_sort_recursive(items, key, ascending, low, pi - 1)
        _quick_sort_recursive(items, key, ascending, pi + 1, high)


def _partition(items, key, ascending, low, high):
    pivot_idx = random.randint(low, high)
    items[pivot_idx], items[high] = items[high], items[pivot_idx]
    pivot = get_value_by_key(items[high], key)
    i = low - 1
    for j in range(low, high):
        val = get_value_by_key(items[j], key)
        if (ascending and val <= pivot) or (not ascending and val >= pivot):
            i += 1
            items[i], items[j] = items[j], items[i]
    items[i + 1], items[high] = items[high], items[i + 1]
    return i + 1


def heap_sort(items, key="amount", ascending=True):
    """Heap sort implementation using max-heap."""
    if len(items) <= 1:
        return items

    items_copy = items.copy()
    n = len(items_copy)

    for i in range(n // 2 - 1, -1, -1):
        _heapify(items_copy, key, ascending, n, i)

    for i in range(n - 1, 0, -1):
        items_copy[i], items_copy[0] = items_copy[0], items_copy[i]
        _heapify(items_copy, key, ascending, i, 0)

    return items_copy


def _heapify(items, key, ascending, n, i):
    extremum = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n:
        left_val = get_value_by_key(items[left], key)
        ext_val = get_value_by_key(items[extremum], key)
        if (ascending and left_val > ext_val) or (not ascending and left_val < ext_val):
            extremum = left

    if right < n:
        right_val = get_value_by_key(items[right], key)
        ext_val = get_value_by_key(items[extremum], key)
        if (ascending and right_val > ext_val) or (not ascending and right_val < ext_val):
            extremum = right

    if extremum != i:
        items[i], items[extremum] = items[extremum], items[i]
        _heapify(items, key, ascending, n, extremum)
