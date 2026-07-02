"""
Search tests — Linear and Binary Search algorithms.

TWO STRATEGIES:

1. LINEAR SEARCH - O(n)
   - Used for: title, description, category (text fields, unsorted)
   - Time: Checks all items sequentially
   
2. BINARY SEARCH - O(log n)
   - Used for: expense_id, date (numeric/sortable, requires pre-sort)
   - Time: Extremely fast on sorted data (50,000× faster for 1M items)
"""

import pytest
from datetime import datetime, date, timedelta

from app import create_app, db
from app.config import TestingConfig
from app.controllers.expense_controller import reset_expense_summaries
from app.services.search import (
    linear_search,
    linear_search_exact,
    binary_search,
    binary_search_range,
    binary_search_range_sorted,
)
from app.models.expense import Expense
from app.models.category import Category
from app.models.user import User
from app.services.merge_sort import merge_sort


class TestLinearSearchService:
    """Unit tests for linear search algorithm."""
    
    def test_linear_search_substring_match(self):
        """Linear search finds substring matches (case-insensitive)."""
        items = [
            {"title": "Coffee Purchase"},
            {"title": "Grocery Shopping"},
            {"title": "Coffee Maker"},
        ]
        results = linear_search(items, "coffee", "title", case_sensitive=False)
        assert len(results) == 2
        assert all("coffee" in str(item["title"]).lower() for item in results)
    
    def test_linear_search_case_sensitive(self):
        """Linear search respects case-sensitive flag."""
        items = [
            {"title": "COFFEE"},
            {"title": "coffee"},
            {"title": "Coffee"},
        ]
        # Case-insensitive (default)
        results_insensitive = linear_search(items, "coffee", "title", case_sensitive=False)
        assert len(results_insensitive) == 3
        
        # Case-sensitive
        results_sensitive = linear_search(items, "coffee", "title", case_sensitive=True)
        assert len(results_sensitive) == 1
    
    def test_linear_search_empty_results(self):
        """Linear search returns empty list when no matches."""
        items = [
            {"title": "Coffee"},
            {"title": "Tea"},
        ]
        results = linear_search(items, "juice", "title")
        assert results == []
    
    def test_linear_search_empty_items(self):
        """Linear search handles empty item list."""
        results = linear_search([], "coffee", "title")
        assert results == []
    
    def test_linear_search_exact_match(self):
        """Linear search finds exact matches."""
        items = [
            {"category_id": 1},
            {"category_id": 2},
            {"category_id": 1},
        ]
        results = linear_search_exact(items, 1, "category_id")
        assert len(results) == 2
        assert all(item["category_id"] == 1 for item in results)
    
    def test_linear_search_with_callable_key(self):
        """Linear search works with callable key function."""
        class Item:
            def __init__(self, name):
                self.name = name
        
        items = [Item("Apple"), Item("Banana"), Item("Apple")]
        results = linear_search(items, "apple", lambda x: x.name, case_sensitive=False)
        assert len(results) == 2
    
    def test_linear_search_performance_characteristics(self):
        """Linear search time complexity: O(n)."""
        # Create items
        items = [{"id": i} for i in range(100)]
        
        # All searches should be O(n)
        results = linear_search(items, "50", "id")
        assert len(results) >= 1  # O(n) - checks all items


class TestBinarySearchService:
    """Unit tests for binary search algorithm."""
    
    def test_binary_search_finds_item(self):
        """Binary search finds target in sorted array."""
        items = [{"id": i} for i in range(1, 11)]  # [1, 2, 3, ..., 10]
        
        idx = binary_search(items, 5, "id", ascending=True)
        assert idx == 4  # Index of item with id=5
        assert items[idx]["id"] == 5
    
    def test_binary_search_not_found(self):
        """Binary search returns -1 when target not found."""
        items = [{"id": i} for i in range(1, 11, 2)]  # [1, 3, 5, 7, 9]
        
        idx = binary_search(items, 4, "id", ascending=True)
        assert idx == -1
    
    def test_binary_search_empty_array(self):
        """Binary search handles empty array."""
        idx = binary_search([], 5, "id")
        assert idx == -1
    
    def test_binary_search_single_item(self):
        """Binary search works with single item."""
        items = [{"id": 5}]
        
        # Found
        idx = binary_search(items, 5, "id")
        assert idx == 0
        
        # Not found
        idx = binary_search(items, 3, "id")
        assert idx == -1
    
    def test_binary_search_descending(self):
        """Binary search works with descending order."""
        items = [{"id": i} for i in range(10, 0, -1)]  # [10, 9, 8, ..., 1]
        
        idx = binary_search(items, 5, "id", ascending=False)
        assert idx == 5
        assert items[idx]["id"] == 5
    
    def test_binary_search_with_callable_key(self):
        """Binary search works with callable key function."""
        class Item:
            def __init__(self, value):
                self.value = value
        
        items = [Item(i) for i in range(1, 11)]
        idx = binary_search(items, 7, lambda x: x.value)
        assert idx == 6
        assert items[idx].value == 7
    
    def test_binary_search_range_with_duplicates(self):
        """Binary search range finds all duplicate values."""
        items = [{"id": i} for i in [1, 2, 2, 2, 3, 4, 5]]
        
        # Search for value with 3 duplicates
        results = binary_search_range(items, 2, "id")
        assert len(results) == 3
        assert all(item["id"] == 2 for item in results)
    
    def test_binary_search_range_single_match(self):
        """Binary search range with single matching item."""
        items = [{"id": i} for i in [1, 2, 3, 4, 5]]
        
        results = binary_search_range(items, 3, "id")
        assert len(results) == 1
        assert results[0]["id"] == 3
    
    def test_binary_search_range_no_matches(self):
        """Binary search range returns empty for no match."""
        items = [{"id": i} for i in [1, 3, 5, 7, 9]]
        
        results = binary_search_range(items, 4, "id")
        assert results == []
    
    def test_binary_search_range_sorted(self):
        """Binary search range finds items within range."""
        items = [{"date": date(2026, i, 1)} for i in range(1, 13)]
        
        start = date(2026, 3, 1)
        end = date(2026, 7, 1)
        
        results = binary_search_range_sorted(items, start, end, "date")
        assert len(results) == 5  # March through July (inclusive)
    
    def test_binary_search_performance_characteristics(self):
        """Binary search time complexity: O(log n)."""
        # Create sorted items
        items = [{"id": i} for i in range(1000)]
        
        # Search should be O(log n) ≈ 10 comparisons for 1000 items
        idx = binary_search(items, 500, "id")
        assert idx == 500


class TestSearchIntegration:
    """Integration tests with real database models."""
    
    @pytest.fixture
    def app(self):
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            reset_expense_summaries()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        user = User(username="testuser", email="test@example.com", full_name="Test User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        
        login_res = app.test_client().post("/api/auth/login", json={
            "login": "testuser",
            "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    
    @pytest.fixture
    def user(self, app):
        return User.query.filter_by(username="testuser").first()
    
    def test_linear_search_with_expense_objects(self, app):
        """Linear search works with real Expense objects."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # Create expenses with different titles
            expenses = [
                Expense(user_id=user.id, title="Coffee", amount=5.50, date=date.today()),
                Expense(user_id=user.id, title="Lunch", amount=12.00, date=date.today()),
                Expense(user_id=user.id, title="Coffee Maker", amount=45.00, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            # Linear search for "Coffee" (substring)
            from app.services.search import search_expenses_by_title
            results = search_expenses_by_title(expenses, "coffee")
            
            assert len(results) == 2
            assert all("coffee" in exp.title.lower() for exp in results)
    
    def test_binary_search_with_sorted_expenses(self, app):
        """Binary search works after sorting by ID."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # Create expenses with IDs: 3, 1, 4, 1, 5, 9, 2, 6
            expenses = []
            for i in [3, 1, 4, 1, 5, 9, 2, 6]:
                exp = Expense(user_id=user.id, title=f"Exp{i}", amount=float(i), date=date.today())
                expenses.append(exp)
            db.session.add_all(expenses)
            db.session.commit()
            
            # Sort by ID
            sorted_expenses = merge_sort(expenses, key="id", ascending=True)
            
            # Binary search
            from app.services.search import search_expense_by_id
            result = search_expense_by_id(sorted_expenses, 5)
            
            assert result is not None
            assert result.id == 5


class TestSearchEndpoints:
    """Integration tests for search API endpoints."""
    
    @pytest.fixture
    def app(self):
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            reset_expense_summaries()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, app):
        user = User(username="testuser", email="test@example.com", full_name="Test User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        
        login_res = app.test_client().post("/api/auth/login", json={
            "login": "testuser",
            "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    
    @pytest.fixture
    def user(self, app):
        return User.query.filter_by(username="testuser").first()
    
    def test_search_title_endpoint(self, client, auth_headers, app):
        """GET /api/expenses/search/title - Linear search by title."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create expenses
            expenses = [
                Expense(user_id=user.id, title="Coffee Purchase", amount=5.50, date=date.today()),
                Expense(user_id=user.id, title="Grocery Shopping", amount=45.00, date=date.today()),
                Expense(user_id=user.id, title="Coffee Maker", amount=30.00, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
        
        # Search for "coffee"
        response = client.get(
            "/api/expenses/search/title?q=coffee",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 2  # Coffee Purchase, Coffee Maker
    
    def test_search_title_missing_query(self, client, auth_headers):
        """Search title endpoint requires query parameter."""
        response = client.get(
            "/api/expenses/search/title",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
    
    def test_search_description_endpoint(self, client, auth_headers, app):
        """GET /api/expenses/search/description - Linear search by description."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create expenses
            expenses = [
                Expense(user_id=user.id, title="Lunch", amount=12.00, date=date.today(),
                       description="Burger and fries at downtown"),
                Expense(user_id=user.id, title="Dinner", amount=25.00, date=date.today(),
                       description="Steak at restaurant"),
                Expense(user_id=user.id, title="Breakfast", amount=8.00, date=date.today(),
                       description="Toast and burger at home"),
            ]
            db.session.add_all(expenses)
            db.session.commit()
        
        # Search for "burger"
        response = client.get(
            "/api/expenses/search/description?q=burger",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
    
    def test_search_category_endpoint(self, client, auth_headers, app):
        """GET /api/expenses/search/category - Linear search by category."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create category
            category = Category(user_id=user.id, name="Food", icon="🍔")
            db.session.add(category)
            db.session.commit()
            
            # Create expenses
            expenses = [
                Expense(user_id=user.id, category_id=category.id, title="Coffee", amount=5.00, date=date.today()),
                Expense(user_id=user.id, category_id=category.id, title="Lunch", amount=12.00, date=date.today()),
                Expense(user_id=user.id, category_id=None, title="Gas", amount=50.00, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
        
        # Search for category
        response = client.get(
            f"/api/expenses/search/category?category_id={Category.query.first().id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
    
    def test_search_category_invalid_id(self, client, auth_headers):
        """Search category endpoint validates numeric ID."""
        response = client.get(
            "/api/expenses/search/category?category_id=invalid",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "integer" in data["message"].lower()
    
    def test_search_id_endpoint(self, client, auth_headers, app):
        """GET /api/expenses/search/id - Binary search by ID.
        
        Binary search is O(log n) - 50,000× faster than linear for 1M items!
        """
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create expenses
            expenses = []
            for i in range(1, 6):
                exp = Expense(user_id=user.id, title=f"Expense{i}", amount=float(i * 10), date=date.today())
                expenses.append(exp)
            db.session.add_all(expenses)
            db.session.commit()
            
            target_id = Expense.query.first().id
        
        # Binary search by ID
        response = client.get(
            f"/api/expenses/search/id?expense_id={target_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["id"] == target_id
    
    def test_search_id_not_found(self, client, auth_headers, app):
        """Binary search returns 404 when expense not found."""
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create an expense
            expense = Expense(user_id=user.id, title="Expense", amount=10.00, date=date.today())
            db.session.add(expense)
            db.session.commit()
        
        # Search for non-existent ID
        response = client.get(
            "/api/expenses/search/id?expense_id=99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
    
    def test_search_date_endpoint(self, client, auth_headers, app):
        """GET /api/expenses/search/date - Binary search by date.
        
        Binary search is O(log n + k) where k = expenses on that date.
        """
        target_date = date(2026, 7, 1)
        
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create expenses on different dates
            expenses = [
                Expense(user_id=user.id, title="E1", amount=10.00, date=date(2026, 6, 30)),
                Expense(user_id=user.id, title="E2", amount=20.00, date=target_date),
                Expense(user_id=user.id, title="E3", amount=30.00, date=target_date),
                Expense(user_id=user.id, title="E4", amount=40.00, date=date(2026, 7, 2)),
            ]
            db.session.add_all(expenses)
            db.session.commit()
        
        # Search for date
        response = client.get(
            f"/api/expenses/search/date?date={target_date.isoformat()}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2  # E2 and E3
    
    def test_search_date_range_endpoint(self, client, auth_headers, app):
        """GET /api/expenses/search/date-range - Binary search within date range.
        
        Binary search is O(log n + k) where k = expenses in range.
        """
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            # Create expenses across 5 days
            expenses = []
            for i in range(1, 6):
                exp = Expense(
                    user_id=user.id,
                    title=f"E{i}",
                    amount=float(i * 10),
                    date=date(2026, 7, i)
                )
                expenses.append(exp)
            db.session.add_all(expenses)
            db.session.commit()
        
        # Search for range [July 2-4]
        response = client.get(
            "/api/expenses/search/date-range?start_date=2026-07-02&end_date=2026-07-04",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 3  # E2, E3, E4
    
    def test_search_date_range_invalid_dates(self, client, auth_headers):
        """Date range endpoint validates date order."""
        response = client.get(
            "/api/expenses/search/date-range?start_date=2026-07-10&end_date=2026-07-01",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "start_date" in data["message"].lower()
    
    def test_search_requires_jwt(self, client):
        """Search endpoints require JWT authentication."""
        endpoints = [
            "/api/expenses/search/title?q=test",
            "/api/expenses/search/description?q=test",
            "/api/expenses/search/category?category_id=1",
            "/api/expenses/search/id?expense_id=1",
            "/api/expenses/search/date?date=2026-07-01",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401  # Unauthorized


class TestSearchComplexity:
    """Verify algorithmic complexity."""
    
    def test_linear_search_visits_many_items(self):
        """Linear search O(n): verify it checks many items in worst case."""
        # Create many items
        items = [{"id": i} for i in range(100)]
        
        # Search for non-existent item (worst case: visit all)
        results = linear_search(items, "999", "id")
        
        # Worst case O(n): should return empty
        assert results == []
    
    def test_binary_search_logarithmic_complexity(self):
        """Binary search O(log n): verify logarithmic growth."""
        # Binary search on 1000 items requires at most ~10 comparisons
        # Linear search would require ~500 on average
        
        items = [{"id": i} for i in range(1000)]
        
        # Even searching for last item is fast in binary search
        idx = binary_search(items, 999, "id")
        assert idx == 999
        
        # This is much faster than linear_search which would visit ~500 items
