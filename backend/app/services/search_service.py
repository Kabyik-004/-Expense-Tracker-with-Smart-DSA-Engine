"""
Search Service
DSA algorithms: Binary Search, Trie-based prefix search
Used for fast lookup of expenses by keyword or amount range.
"""


class TrieNode:
    __slots__ = ("children", "is_end", "expense_ids")

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.expense_ids = []


class Trie:
    """Trie (prefix tree) for fast keyword search on expense titles/descriptions."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, expense_id):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.expense_ids.append(expense_id)

    def search(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect(node)

    def starts_with(self, prefix):
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect(node)

    def _collect(self, node):
        ids = []
        stack = [node]
        while stack:
            current = stack.pop()
            ids.extend(current.expense_ids)
            stack.extend(current.children.values())
        return ids


def build_title_trie(expenses):
    trie = Trie()
    for exp in expenses:
        for word in exp.title.split():
            trie.insert(word, exp.id)
    return trie


def build_description_trie(expenses):
    trie = Trie()
    for exp in expenses:
        if exp.description:
            for word in exp.description.split():
                trie.insert(word, exp.id)
    return trie
