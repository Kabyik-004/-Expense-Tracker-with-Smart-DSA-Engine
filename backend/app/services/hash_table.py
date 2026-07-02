"""
Hash Table implementation using defaultdict.

This module provides a manually implemented hash table that stores aggregated
expense metrics by arbitrary keys. It is used by the expense module to compute
category totals, category counts, and monthly totals efficiently.
"""

from collections import defaultdict


class HashTable:
    def __init__(self):
        self._table = defaultdict(lambda: {"total": 0.0, "count": 0})

    def add(self, key, amount):
        """Add a value for a key.

        Time complexity: O(1) average.
        """
        bucket = self._table[key]
        bucket["total"] += amount
        bucket["count"] += 1

    def remove(self, key, amount):
        """Remove a value for a key.

        Time complexity: O(1) average.
        """
        if key not in self._table:
            return

        bucket = self._table[key]
        bucket["total"] -= amount
        bucket["count"] -= 1

        if bucket["count"] <= 0 and bucket["total"] <= 0:
            del self._table[key]

    def update(self, old_key, new_key, old_amount, new_amount):
        """Update a record by removing the old value and adding the new one.

        Time complexity: O(1) average.
        """
        self.remove(old_key, old_amount)
        self.add(new_key, new_amount)

    def getCategoryTotal(self, key):
        """Return the total amount for a given key.

        Time complexity: O(1) average.
        """
        return self._table.get(key, {"total": 0.0})["total"]

    def getCategoryCount(self, key):
        """Return the count for a given key."""
        return self._table.get(key, {"count": 0})["count"]

    def to_dict(self):
        """Return a snapshot of the hash table."""
        return {
            str(key): {"total": value["total"], "count": value["count"]}
            for key, value in self._table.items()
        }
