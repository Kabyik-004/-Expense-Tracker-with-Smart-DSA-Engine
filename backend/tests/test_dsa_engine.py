"""Comprehensive tests for all DSA engine services."""

from datetime import date

from app.services.budget_optimizer import knapsack_optimize, greedy_budget_allocation
from app.services.graph_service import SpendingGraph, build_spending_graph
from app.services.search_service import Trie, build_title_trie, build_description_trie
from app.services.sorting_service import quick_sort, heap_sort


class TestBudgetOptimizer:
    """Tests for 0/1 Knapsack DP and Greedy budget allocation."""

    def test_knapsack_basic(self):
        categories = [
            {"name": "Food", "budget_limit": 500, "priority": 8},
            {"name": "Transport", "budget_limit": 200, "priority": 5},
            {"name": "Entertainment", "budget_limit": 300, "priority": 3},
        ]
        result = knapsack_optimize(categories, 700)
        assert len(result["selected"]) > 0
        assert result["total_allocated"] <= 700
        assert result["total_priority"] > 0

    def test_knapsack_exact_budget(self):
        categories = [
            {"name": "A", "budget_limit": 100, "priority": 5},
            {"name": "B", "budget_limit": 200, "priority": 10},
        ]
        result = knapsack_optimize(categories, 300)
        assert result["total_allocated"] == 300
        assert result["total_priority"] == 15

    def test_knapsack_prioritizes_high_value(self):
        categories = [
            {"name": "High", "budget_limit": 100, "priority": 10},
            {"name": "Low", "budget_limit": 100, "priority": 1},
        ]
        result = knapsack_optimize(categories, 100)
        assert result["selected"][0]["name"] == "High"

    def test_knapsack_no_budget(self):
        result = knapsack_optimize([{"name": "A", "budget_limit": 100, "priority": 5}], 0)
        assert result["total_allocated"] == 0

    def test_knapsack_empty_categories(self):
        result = knapsack_optimize([], 1000)
        assert result["selected"] == []
        assert result["total_allocated"] == 0

    def test_knapsack_single_category(self):
        categories = [{"name": "Only", "budget_limit": 500, "priority": 7}]
        result = knapsack_optimize(categories, 300)
        assert len(result["selected"]) == 1
        assert result["selected"][0]["name"] == "Only"

    def test_knapsack_small_budget_one_fits(self):
        categories = [
            {"name": "Big", "budget_limit": 1000, "priority": 5},
            {"name": "Small", "budget_limit": 100, "priority": 10},
        ]
        result = knapsack_optimize(categories, 50)
        assert result["total_allocated"] <= 50
        assert result["total_priority"] > 0

    def test_greedy_basic(self):
        categories = [
            {"name": "Food", "budget_limit": 500, "priority": 8},
            {"name": "Transport", "budget_limit": 200, "priority": 5},
        ]
        result = greedy_budget_allocation(categories, 600)
        assert len(result) > 0

    def test_greedy_exceeds_budget(self):
        categories = [
            {"name": "Big", "budget_limit": 1000, "priority": 5},
        ]
        result = greedy_budget_allocation(categories, 500)
        assert len(result) == 0

    def test_greedy_empty(self):
        result = greedy_budget_allocation([], 1000)
        assert result == []

    def test_greedy_zero_budget(self):
        result = greedy_budget_allocation([{"name": "A", "budget_limit": 100, "priority": 5}], 0)
        assert result == []


class TestSpendingGraph:
    """Tests for adjacency list graph with BFS/DFS traversal."""

    def test_add_edge(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        assert 2 in g.adjacency[1]
        assert 1 in g.adjacency[2]
        assert g.adjacency[1][2] == 1

    def test_add_edge_weight_increment(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 2)
        assert g.adjacency[1][2] == 2

    def test_bfs_single_node(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        order = g.bfs(1)
        assert order == [1, 2]

    def test_bfs_multiple_nodes(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 3)
        g.add_edge(2, 4)
        order = g.bfs(1)
        assert order[0] == 1
        assert order[-1] == 4

    def test_bfs_disconnected(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        g.add_edge(3, 4)
        order = g.bfs(1)
        assert order == [1, 2]
        assert 3 not in order
        assert 4 not in order

    def test_dfs_single_node(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        order = g.dfs(1)
        assert order[0] == 1
        assert 2 in order

    def test_dfs_multiple_nodes(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        g.add_edge(1, 3)
        g.add_edge(2, 4)
        order = g.dfs(1)
        assert order[0] == 1
        assert len(order) == 4

    def test_bfs_start_node_not_in_graph(self):
        g = SpendingGraph()
        order = g.bfs(99)
        assert order == [99]

    def test_dfs_start_node_not_in_graph(self):
        g = SpendingGraph()
        order = g.dfs(99)
        assert order == [99]

    def test_get_strongly_connected_empty(self):
        g = SpendingGraph()
        g.add_edge(1, 2)
        clusters = g.get_strongly_connected(min_weight=5)
        assert clusters == []

    def test_get_strongly_connected_basic(self):
        g = SpendingGraph()
        for _ in range(3):
            g.add_edge(1, 2)
        clusters = g.get_strongly_connected(min_weight=2)
        assert len(clusters) > 0

    def test_build_spending_graph(self):
        class MockExpense:
            def __init__(self, category_id, date_val):
                self.category_id = category_id
                self.date = date_val
        expenses = [
            MockExpense(1, date(2026, 7, 1)),
            MockExpense(2, date(2026, 7, 1)),
            MockExpense(1, date(2026, 7, 2)),
        ]
        graph = build_spending_graph(expenses)
        assert 1 in graph.adjacency
        assert 2 in graph.adjacency
        assert graph.adjacency[1][2] >= 1

    def test_build_spending_graph_no_category(self):
        expenses = [
            type("Expense", (), {"category_id": None, "date": date(2026, 7, 1), "title": "NoCat"})(),
        ]
        graph = build_spending_graph(expenses)
        assert len(graph.adjacency) == 0


class TestTrie:
    """Tests for Trie (prefix tree) data structure."""

    def test_insert_and_search(self):
        trie = Trie()
        trie.insert("hello", 1)
        trie.insert("world", 2)
        results = trie.search("hello")
        assert 1 in results

    def test_search_nonexistent(self):
        trie = Trie()
        trie.insert("hello", 1)
        results = trie.search("world")
        assert results == []

    def test_starts_with(self):
        trie = Trie()
        trie.insert("hello", 1)
        trie.insert("help", 2)
        trie.insert("heap", 3)
        results = trie.starts_with("hel")
        assert len(results) == 2
        assert 1 in results
        assert 2 in results

    def test_starts_with_no_match(self):
        trie = Trie()
        trie.insert("hello", 1)
        results = trie.starts_with("xyz")
        assert results == []

    def test_multiple_ids_same_word(self):
        trie = Trie()
        trie.insert("test", 1)
        trie.insert("test", 2)
        trie.insert("test", 3)
        results = trie.search("test")
        assert len(results) == 3

    def test_case_insensitive(self):
        trie = Trie()
        trie.insert("Hello", 1)
        assert trie.search("hello") == [1]
        assert trie.search("HELLO") == [1]

    def test_empty_string(self):
        trie = Trie()
        trie.insert("", 1)
        assert trie.search("") == [1]

    def test_build_title_trie(self):
        class MockExpense:
            def __init__(self, id, title):
                self.id = id
                self.title = title
        expenses = [
            MockExpense(1, "coffee morning"),
            MockExpense(2, "morning tea"),
        ]
        trie = build_title_trie(expenses)
        results = trie.search("coffee")
        assert len(results) == 1
        results = trie.search("morning")
        assert len(results) == 2

    def test_build_description_trie_empty(self):
        class MockExpense:
            def __init__(self, id, title, description):
                self.id = id
                self.title = title
                self.description = description
        expenses = [MockExpense(1, "Test", None)]
        trie = build_description_trie(expenses)
        results = trie.search("anything")
        assert results == []

    def test_starts_with_prefix_matches_many(self):
        trie = Trie()
        for i in range(10):
            trie.insert(f"item{i}", i)
        results = trie.starts_with("item")
        assert len(results) == 10


class TestSortingService:
    """Tests for Quick Sort and Heap Sort implementations."""

    def test_quick_sort_basic_ascending(self):
        items = [{"amount": 30}, {"amount": 10}, {"amount": 20}]
        result = quick_sort(items, key="amount", ascending=True)
        assert [r["amount"] for r in result] == [10, 20, 30]

    def test_quick_sort_descending(self):
        items = [{"amount": 10}, {"amount": 30}, {"amount": 20}]
        result = quick_sort(items, key="amount", ascending=False)
        assert [r["amount"] for r in result] == [30, 20, 10]

    def test_quick_sort_empty(self):
        assert quick_sort([], key="amount") == []

    def test_quick_sort_single(self):
        assert quick_sort([{"amount": 42}], key="amount") == [{"amount": 42}]

    def test_quick_sort_duplicates(self):
        items = [{"amount": 5}, {"amount": 5}, {"amount": 3}]
        result = quick_sort(items, key="amount")
        assert [r["amount"] for r in result] == [3, 5, 5]

    def test_quick_sort_already_sorted(self):
        items = [{"amount": 1}, {"amount": 2}, {"amount": 3}]
        result = quick_sort(items, key="amount")
        assert [r["amount"] for r in result] == [1, 2, 3]

    def test_heap_sort_basic_ascending(self):
        items = [{"amount": 30}, {"amount": 10}, {"amount": 20}]
        result = heap_sort(items, key="amount", ascending=True)
        assert [r["amount"] for r in result] == [10, 20, 30]

    def test_heap_sort_descending(self):
        items = [{"amount": 10}, {"amount": 30}, {"amount": 20}]
        result = heap_sort(items, key="amount", ascending=False)
        assert [r["amount"] for r in result] == [30, 20, 10]

    def test_heap_sort_empty(self):
        assert heap_sort([], key="amount") == []

    def test_heap_sort_single(self):
        assert heap_sort([{"amount": 42}], key="amount") == [{"amount": 42}]

    def test_heap_sort_duplicates(self):
        items = [{"amount": 5}, {"amount": 5}, {"amount": 3}]
        result = heap_sort(items, key="amount")
        assert [r["amount"] for r in result] == [3, 5, 5]

    def test_sort_by_title_alphabetical(self):
        items = [{"title": "Zebra"}, {"title": "Apple"}, {"title": "Monkey"}]
        result = quick_sort(items, key="title")
        assert [r["title"] for r in result] == ["Apple", "Monkey", "Zebra"]

    def test_sort_by_title_descending(self):
        items = [{"title": "Apple"}, {"title": "Zebra"}]
        result = heap_sort(items, key="title", ascending=False)
        assert [r["title"] for r in result] == ["Zebra", "Apple"]

    def test_sort_with_callable_key(self):
        items = [{"val": 3}, {"val": 1}, {"val": 2}]
        result = quick_sort(items, key=lambda x: x["val"])
        assert [r["val"] for r in result] == [1, 2, 3]

    def test_sort_with_callable_heap(self):
        items = [{"val": 3}, {"val": 1}, {"val": 2}]
        result = heap_sort(items, key=lambda x: x["val"])
        assert [r["val"] for r in result] == [1, 2, 3]
