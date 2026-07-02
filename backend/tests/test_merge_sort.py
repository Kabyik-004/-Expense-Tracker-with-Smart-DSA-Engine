"""Tests for merge sort implementation and expense sorting endpoints."""

import pytest
from datetime import datetime, date

from app import create_app, db
from app.config import TestingConfig
from app.controllers.expense_controller import reset_expense_summaries
from app.models.user import User
from app.models.expense import Expense
from app.services.merge_sort import (
    merge_sort,
    sort_expenses,
    sort_expenses_multi,
    explain_recursion,
)


class TestMergeSortService:
    """Unit tests for merge sort algorithm implementation."""

    def test_merge_sort_basic_ascending(self):
        """Test basic merge sort in ascending order."""
        items = [38, 27, 43, 3, 9, 82, 10]
        result = merge_sort(items.copy(), key=lambda x: x, ascending=True)
        assert result == [3, 9, 10, 27, 38, 43, 82]

    def test_merge_sort_basic_descending(self):
        """Test basic merge sort in descending order."""
        items = [38, 27, 43, 3, 9, 82, 10]
        result = merge_sort(items.copy(), key=lambda x: x, ascending=False)
        assert result == [82, 43, 38, 27, 10, 9, 3]

    def test_merge_sort_empty(self):
        """Test merge sort with empty list."""
        items = []
        result = merge_sort(items.copy(), key=lambda x: x, ascending=True)
        assert result == []

    def test_merge_sort_single_element(self):
        """Test merge sort with single element."""
        items = [42]
        result = merge_sort(items.copy(), key=lambda x: x, ascending=True)
        assert result == [42]

    def test_merge_sort_duplicates(self):
        """Test merge sort with duplicate values (stable sort)."""
        items = [5, 2, 8, 2, 9, 1, 5]
        result = merge_sort(items.copy(), key=lambda x: x, ascending=True)
        assert result == [1, 2, 2, 5, 5, 8, 9]

    def test_merge_sort_already_sorted(self):
        """Test merge sort with already sorted array."""
        items = [1, 2, 3, 4, 5]
        result = merge_sort(items.copy(), key=lambda x: x, ascending=True)
        assert result == [1, 2, 3, 4, 5]

    def test_merge_sort_reverse_sorted(self):
        """Test merge sort with reverse sorted array."""
        items = [5, 4, 3, 2, 1]
        result = merge_sort(items.copy(), key=lambda x: x, ascending=True)
        assert result == [1, 2, 3, 4, 5]

    def test_merge_sort_dict_objects(self):
        """Test merge sort with dictionary objects."""
        items = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ]
        result = merge_sort(items.copy(), key="age", ascending=True)
        assert result[0]["age"] == 25
        assert result[1]["age"] == 30
        assert result[2]["age"] == 35

    def test_merge_sort_stability(self):
        """Test that merge sort is stable (preserves order of equal elements)."""
        items = [
            {"id": 1, "value": 5},
            {"id": 2, "value": 3},
            {"id": 3, "value": 5},
            {"id": 4, "value": 1},
        ]
        result = merge_sort(items.copy(), key="value", ascending=True)
        # Elements with value=5: should maintain id order (1 before 3)
        value_5_ids = [item["id"] for item in result if item["value"] == 5]
        assert value_5_ids == [1, 3]

    def test_explain_recursion_callable(self):
        """Test that explain_recursion documentation exists."""
        assert callable(explain_recursion)
        assert explain_recursion.__doc__ is not None
        assert "Recursion" in explain_recursion.__doc__


class TestSortExpensesFunction:
    """Unit tests for sort_expenses wrapper function."""

    def test_sort_expenses_empty(self):
        """Test sorting empty expense list."""
        result = sort_expenses([], sort_by="amount")
        assert result == []

    def test_sort_expenses_by_amount(self):
        """Test sorting expenses by amount."""
        expenses = [
            Expense(id=1, amount=50.0),
            Expense(id=2, amount=30.0),
            Expense(id=3, amount=80.0),
        ]
        result = sort_expenses(expenses, sort_by="amount", ascending=True)
        assert result[0].amount == 30.0
        assert result[1].amount == 50.0
        assert result[2].amount == 80.0

    def test_sort_expenses_by_title(self):
        """Test sorting expenses by title."""
        expenses = [
            Expense(id=1, title="Zebra"),
            Expense(id=2, title="Apple"),
            Expense(id=3, title="Mango"),
        ]
        result = sort_expenses(expenses, sort_by="title", ascending=True)
        assert result[0].title == "Apple"
        assert result[1].title == "Mango"
        assert result[2].title == "Zebra"

    def test_sort_expenses_multi_field(self):
        """Test sorting expenses by multiple fields."""
        expenses = [
            Expense(id=1, category_id=2, amount=50.0),
            Expense(id=2, category_id=1, amount=80.0),
            Expense(id=3, category_id=1, amount=30.0),
            Expense(id=4, category_id=2, amount=40.0),
        ]
        # Sort by category_id asc, then amount desc
        result = sort_expenses_multi(
            expenses,
            sort_fields=["category_id", "amount"],
            ascending_list=[True, False],
        )
        # Category 1 first, then category 2
        assert result[0].category_id == 1
        assert result[1].category_id == 1
        # Within category 1: amount 80 before 30
        assert result[0].amount == 80.0
        assert result[1].amount == 30.0
        # Category 2: amount 50 before 40
        assert result[2].amount == 50.0
        assert result[3].amount == 40.0


class TestExpenseSortingEndpoints:
    """Integration tests for expense sorting endpoints."""

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
        user = User(username="sortuser", email="sort@example.com", full_name="Sort User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()

        login_res = app.test_client().post(
            "/api/auth/login",
            json={"login": "sortuser", "password": "TestPass1"},
        )
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def test_sort_single_by_amount_ascending(self, client, auth_headers):
        """Test sorting expenses by amount in ascending order."""
        # Create expenses
        for amount in [50, 30, 80]:
            client.post(
                "/api/expenses/",
                json={"title": f"Expense", "amount": amount, "date": "2026-07-01"},
                headers=auth_headers,
            )

        res = client.get("/api/expenses/sort/single?sort_by=amount&ascending=true", headers=auth_headers)
        assert res.status_code == 200
        expenses = res.get_json()["data"]["expenses"]
        assert expenses[0]["amount"] == 30.0
        assert expenses[1]["amount"] == 50.0
        assert expenses[2]["amount"] == 80.0

    def test_sort_single_by_amount_descending(self, client, auth_headers):
        """Test sorting expenses by amount in descending order."""
        # Create expenses
        for amount in [50, 30, 80]:
            client.post(
                "/api/expenses/",
                json={"title": f"Expense", "amount": amount, "date": "2026-07-01"},
                headers=auth_headers,
            )

        res = client.get("/api/expenses/sort/single?sort_by=amount&ascending=false", headers=auth_headers)
        assert res.status_code == 200
        expenses = res.get_json()["data"]["expenses"]
        assert expenses[0]["amount"] == 80.0
        assert expenses[1]["amount"] == 50.0
        assert expenses[2]["amount"] == 30.0

    def test_sort_single_by_title(self, client, auth_headers):
        """Test sorting expenses by title."""
        titles = ["Zebra Expense", "Apple Expense", "Mango Expense"]
        for title in titles:
            client.post(
                "/api/expenses/",
                json={"title": title, "amount": 10.0, "date": "2026-07-01"},
                headers=auth_headers,
            )

        res = client.get("/api/expenses/sort/single?sort_by=title&ascending=true", headers=auth_headers)
        assert res.status_code == 200
        expenses = res.get_json()["data"]["expenses"]
        assert expenses[0]["title"] == "Apple Expense"
        assert expenses[1]["title"] == "Mango Expense"
        assert expenses[2]["title"] == "Zebra Expense"

    def test_sort_single_by_date(self, client, auth_headers):
        """Test sorting expenses by date."""
        dates = ["2026-07-03", "2026-07-01", "2026-07-02"]
        for i, date_str in enumerate(dates):
            client.post(
                "/api/expenses/",
                json={"title": f"Expense {i}", "amount": 10.0, "date": date_str},
                headers=auth_headers,
            )

        res = client.get("/api/expenses/sort/single?sort_by=date&ascending=true", headers=auth_headers)
        assert res.status_code == 200
        expenses = res.get_json()["data"]["expenses"]
        assert expenses[0]["date"] == "2026-07-01"
        assert expenses[1]["date"] == "2026-07-02"
        assert expenses[2]["date"] == "2026-07-03"

    def test_sort_multi_field(self, client, auth_headers):
        """Test sorting by multiple fields."""
        expenses_data = [
            {"title": "Exp1", "amount": 50.0, "date": "2026-07-01", "category_id": 2},
            {"title": "Exp2", "amount": 80.0, "date": "2026-07-01", "category_id": 1},
            {"title": "Exp3", "amount": 30.0, "date": "2026-07-01", "category_id": 1},
            {"title": "Exp4", "amount": 40.0, "date": "2026-07-01", "category_id": 2},
        ]
        for exp in expenses_data:
            client.post("/api/expenses/", json=exp, headers=auth_headers)

        res = client.post(
            "/api/expenses/sort/multi",
            json={
                "sort_fields": ["category_id", "amount"],
                "ascending": [True, False],
            },
            headers=auth_headers,
        )
        assert res.status_code == 200
        expenses = res.get_json()["data"]["expenses"]
        # Category 1 first, sorted by amount descending
        assert expenses[0]["category_id"] == 1
        assert expenses[0]["amount"] == 80.0
        assert expenses[1]["category_id"] == 1
        assert expenses[1]["amount"] == 30.0
        # Category 2 next, sorted by amount descending
        assert expenses[2]["category_id"] == 2
        assert expenses[2]["amount"] == 50.0
        assert expenses[3]["category_id"] == 2
        assert expenses[3]["amount"] == 40.0

    def test_sort_invalid_field(self, client, auth_headers):
        """Test sorting with invalid field name."""
        # Create an expense first
        client.post(
            "/api/expenses/",
            json={"title": "Test", "amount": 10.0, "date": "2026-07-01"},
            headers=auth_headers,
        )

        res = client.get("/api/expenses/sort/single?sort_by=invalid_field&ascending=true", headers=auth_headers)
        assert res.status_code == 400
        assert "Invalid sort field" in res.get_json()["message"]

    def test_sort_empty_expense_list(self, client, auth_headers):
        """Test sorting with no expenses."""
        res = client.get("/api/expenses/sort/single?sort_by=amount&ascending=true", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["data"]["expenses"] == []
