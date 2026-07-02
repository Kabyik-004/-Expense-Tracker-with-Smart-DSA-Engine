"""Tests for expense endpoints."""

import pytest

from app import create_app, db
from app.config import TestingConfig
from app.controllers.expense_controller import reset_expense_summaries
from app.models.user import User


class TestExpenseEndpoints:

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
        user = User(username="expenseuser", email="expense@example.com", full_name="Expense User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()

        login_res = app.test_client().post("/api/auth/login", json={
            "login": "expenseuser",
            "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def test_create_expense(self, client, auth_headers):
        res = client.post(
            "/api/expenses/",
            json={
                "title": "Lunch",
                "amount": 12.5,
                "description": "Team lunch",
                "date": "2026-07-01",
                "payment_method": "card",
            },
            headers=auth_headers,
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["expense"]["title"] == "Lunch"

    def test_list_expenses(self, client, auth_headers):
        client.post(
            "/api/expenses/",
            json={
                "title": "Coffee",
                "amount": 3.5,
                "date": "2026-07-01",
            },
            headers=auth_headers,
        )
        res = client.get("/api/expenses/", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.get_json()["data"]["expenses"]) == 1

    def test_get_expense_by_id(self, client, auth_headers):
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Taxi", "amount": 20.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["data"]["expense"]["id"] == expense_id

    def test_update_expense(self, client, auth_headers):
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Dinner", "amount": 45.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        res = client.put(
            f"/api/expenses/{expense_id}",
            json={"amount": 50.0, "notes": "Updated amount"},
            headers=auth_headers,
        )
        assert res.status_code == 200
        updated = res.get_json()["data"]["expense"]
        assert updated["amount"] == 50.0
        assert updated["notes"] == "Updated amount"

    def test_delete_expense(self, client, auth_headers):
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Snack", "amount": 5.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        res = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert res.status_code == 200

        res2 = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert res2.status_code == 404

    def test_summary_endpoints(self, client, auth_headers):
        client.post(
            "/api/expenses/",
            json={"title": "Breakfast", "amount": 10.0, "date": "2026-07-01", "category_id": 1},
            headers=auth_headers,
        )
        client.post(
            "/api/expenses/",
            json={"title": "Lunch", "amount": 20.0, "date": "2026-07-01", "category_id": 1},
            headers=auth_headers,
        )
        client.post(
            "/api/expenses/",
            json={"title": "Dinner", "amount": 30.0, "date": "2026-08-01", "category_id": 2},
            headers=auth_headers,
        )

        res_cat_totals = client.get("/api/expenses/summary/category-totals", headers=auth_headers)
        res_cat_counts = client.get("/api/expenses/summary/category-counts", headers=auth_headers)
        res_month_totals = client.get("/api/expenses/summary/monthly-totals", headers=auth_headers)

        assert res_cat_totals.status_code == 200
        assert res_cat_counts.status_code == 200
        assert res_month_totals.status_code == 200

        assert res_cat_totals.get_json()["data"]["category_totals"]["1"]["total"] == 30.0
        assert res_cat_counts.get_json()["data"]["category_counts"]["1"]["count"] == 2
        assert res_month_totals.get_json()["data"]["monthly_totals"]["2026-07"]["total"] == 30.0
