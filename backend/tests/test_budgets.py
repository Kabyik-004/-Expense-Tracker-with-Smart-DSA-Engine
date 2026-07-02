"""Tests for budget CRUD and status endpoints."""

import pytest
from datetime import datetime, timezone

from app import create_app, db
from app.config import TestingConfig
from app.models.user import User
from app.models.budget import Budget
from app.models.category import Category


class TestBudgetEndpoints:
    """API tests for budget endpoints."""

    @pytest.fixture
    def app(self):
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, app):
        user = User(username="budgetuser", email="budget@example.com", full_name="Budget User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        login_res = app.test_client().post("/api/auth/login", json={
            "login": "budgetuser", "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    @pytest.fixture
    def sample_category(self, app):
        user = User.query.filter_by(username="budgetuser").first()
        cat = Category(user_id=user.id, name="Food", icon="🍔", color="#ff0000", budget_limit=500)
        db.session.add(cat)
        db.session.commit()
        return cat

    def test_set_budget_success(self, client, auth_headers, sample_category):
        res = client.post("/api/budgets/", json={
            "amount": 1000,
            "month": 7,
            "year": 2026,
            "category_id": sample_category.id,
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["budget"]["amount"] == 1000

    def test_set_overall_budget(self, client, auth_headers):
        res = client.post("/api/budgets/", json={
            "amount": 5000,
            "month": 7,
            "year": 2026,
            "category_id": None,
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["budget"]["category_id"] is None

    def test_update_budget(self, client, auth_headers, sample_category):
        client.post("/api/budgets/", json={
            "amount": 1000, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        res = client.post("/api/budgets/", json={
            "amount": 2000, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["data"]["budget"]["amount"] == 2000

    def test_get_budget_status(self, client, auth_headers, sample_category):
        client.post("/api/budgets/", json={
            "amount": 1000, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        res = client.get("/api/budgets/status?month=7&year=2026", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["total_budget"] == 1000
        assert data["data"]["month"] == 7
        assert data["data"]["year"] == 2026

    def test_get_budget_status_default_month(self, client, auth_headers):
        now = datetime.now(timezone.utc)
        res = client.get("/api/budgets/status", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["month"] == int(now.strftime("%m"))
        assert data["data"]["year"] == int(now.strftime("%Y"))

    def test_list_budgets(self, client, auth_headers, sample_category):
        client.post("/api/budgets/", json={
            "amount": 1000, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        client.post("/api/budgets/", json={
            "amount": 500, "month": 8, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        res = client.get("/api/budgets/", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["data"]["budgets"]) == 2

    def test_delete_budget(self, client, auth_headers, sample_category):
        create_res = client.post("/api/budgets/", json={
            "amount": 1000, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        budget_id = create_res.get_json()["data"]["budget"]["id"]
        res = client.delete(f"/api/budgets/{budget_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["success"] is True
        res = client.delete(f"/api/budgets/{budget_id}", headers=auth_headers)
        assert res.status_code == 404

    def test_budget_status_with_spending(self, client, auth_headers, sample_category):
        client.post("/api/budgets/", json={
            "amount": 100, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        client.post("/api/expenses/", json={
            "title": "Lunch", "amount": 30, "date": "2026-07-05", "category_id": sample_category.id,
        }, headers=auth_headers)
        client.post("/api/expenses/", json={
            "title": "Dinner", "amount": 50, "date": "2026-07-10", "category_id": sample_category.id,
        }, headers=auth_headers)
        res = client.get("/api/budgets/status?month=7&year=2026", headers=auth_headers)
        data = res.get_json()["data"]
        assert data["total_spent"] == 80
        assert data["total_remaining"] == 20
        assert data["overall_percentage"] == 80.0
        assert data["overall_warning"] is True

    def test_budget_exceeded(self, client, auth_headers, sample_category):
        client.post("/api/budgets/", json={
            "amount": 50, "month": 7, "year": 2026, "category_id": sample_category.id,
        }, headers=auth_headers)
        client.post("/api/expenses/", json={
            "title": "Shopping", "amount": 60, "date": "2026-07-05", "category_id": sample_category.id,
        }, headers=auth_headers)
        res = client.get("/api/budgets/status?month=7&year=2026", headers=auth_headers)
        data = res.get_json()["data"]
        assert data["overall_exceeded"] is True
        assert data["budgets"][0]["exceeded"] is True

    def test_budget_validation_negative_amount(self, client, auth_headers):
        res = client.post("/api/budgets/", json={
            "amount": -100, "month": 7, "year": 2026,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_budget_validation_invalid_month(self, client, auth_headers):
        res = client.post("/api/budgets/", json={
            "amount": 100, "month": 13, "year": 2026,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_budget_validation_missing_amount(self, client, auth_headers):
        res = client.post("/api/budgets/", json={
            "month": 7, "year": 2026,
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_budget_requires_jwt(self, client):
        endpoints = [
            ("GET", "/api/budgets/"),
            ("GET", "/api/budgets/status"),
            ("POST", "/api/budgets/"),
        ]
        for method, url in endpoints:
            if method == "GET":
                res = client.get(url)
            else:
                res = client.post(url, json={})
            assert res.status_code == 401
