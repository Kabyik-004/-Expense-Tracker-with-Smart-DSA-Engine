"""
Tests for income CRUD endpoints.
Includes undo functionality tests.
"""

import pytest

from app import create_app, db
from app.config import TestingConfig
from app.models.user import User


class TestIncomeEndpoints:

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
        user = User(username="incomeuser", email="income@example.com", full_name="Income User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        login_res = app.test_client().post("/api/auth/login", json={
            "login": "incomeuser", "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def test_create_income(self, client, auth_headers):
        res = client.post("/api/incomes/", json={
            "source": "Salary", "amount": 1500.5, "description": "July salary", "date": "2026-07-01",
        }, headers=auth_headers)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["income"]["source"] == "Salary"
        assert data["data"]["income"]["amount"] == 1500.5

    def test_get_incomes(self, client, auth_headers):
        client.post("/api/incomes/", json={
            "source": "Freelance", "amount": 500.0, "description": "Consulting", "date": "2026-07-01",
        }, headers=auth_headers)
        res = client.get("/api/incomes/", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.get_json()["data"]["incomes"]) == 1

    def test_get_income_by_id(self, client, auth_headers):
        create_res = client.post("/api/incomes/", json={
            "source": "Investment", "amount": 250.75, "description": "Dividend", "date": "2026-07-01",
        }, headers=auth_headers)
        income_id = create_res.get_json()["data"]["income"]["id"]
        res = client.get(f"/api/incomes/{income_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["data"]["income"]["id"] == income_id

    def test_update_income(self, client, auth_headers):
        create_res = client.post("/api/incomes/", json={
            "source": "Bonus", "amount": 1000.0, "description": "Performance bonus", "date": "2026-07-01",
        }, headers=auth_headers)
        income_id = create_res.get_json()["data"]["income"]["id"]
        res = client.put(f"/api/incomes/{income_id}", json={
            "amount": 1200.0, "description": "Updated bonus",
        }, headers=auth_headers)
        assert res.status_code == 200
        updated = res.get_json()["data"]["income"]
        assert updated["amount"] == 1200.0
        assert updated["description"] == "Updated bonus"

    def test_delete_income(self, client, auth_headers):
        create_res = client.post("/api/incomes/", json={
            "source": "Gift", "amount": 250.0, "description": "Birthday gift", "date": "2026-07-01",
        }, headers=auth_headers)
        income_id = create_res.get_json()["data"]["income"]["id"]
        res = client.delete(f"/api/incomes/{income_id}", headers=auth_headers)
        assert res.status_code == 200
        res2 = client.get(f"/api/incomes/{income_id}", headers=auth_headers)
        assert res2.status_code == 404

    def test_income_not_found(self, client, auth_headers):
        res = client.get("/api/incomes/99999", headers=auth_headers)
        assert res.status_code == 404
        res = client.put("/api/incomes/99999", json={"amount": 100}, headers=auth_headers)
        assert res.status_code == 404
        res = client.delete("/api/incomes/99999", headers=auth_headers)
        assert res.status_code == 404

    def test_create_income_validation(self, client, auth_headers):
        res = client.post("/api/incomes/", json={
            "amount": 100, "date": "2026-07-01",
        }, headers=auth_headers)
        assert res.status_code == 400
        res = client.post("/api/incomes/", json={
            "source": "Test", "date": "2026-07-01",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_undo_income_create(self, client, auth_headers):
        create_res = client.post("/api/incomes/", json={
            "source": "Temp", "amount": 500, "date": "2026-07-01",
        }, headers=auth_headers)
        income_id = create_res.get_json()["data"]["income"]["id"]
        get_res = client.get(f"/api/incomes/{income_id}", headers=auth_headers)
        assert get_res.status_code == 200
        undo_res = client.post("/api/incomes/undo", headers=auth_headers)
        assert undo_res.status_code == 200
        get_res = client.get(f"/api/incomes/{income_id}", headers=auth_headers)
        assert get_res.status_code == 404

    def test_undo_income_delete(self, client, auth_headers):
        create_res = client.post("/api/incomes/", json={
            "source": "Temp", "amount": 500, "date": "2026-07-01",
        }, headers=auth_headers)
        income_id = create_res.get_json()["data"]["income"]["id"]
        client.delete(f"/api/incomes/{income_id}", headers=auth_headers)
        undo_res = client.post("/api/incomes/undo", headers=auth_headers)
        assert undo_res.status_code == 200
        get_res = client.get(f"/api/incomes/{income_id}", headers=auth_headers)
        assert get_res.status_code == 200

    def test_undo_income_empty_stack(self, client, auth_headers):
        res = client.post("/api/incomes/undo", headers=auth_headers)
        assert res.status_code == 400

    def test_incomes_requires_jwt(self, client):
        endpoints = [
            ("GET", "/api/incomes/"),
            ("POST", "/api/incomes/"),
            ("POST", "/api/incomes/undo"),
        ]
        for method, url in endpoints:
            res = client.get(url) if method == "GET" else client.post(url, json={})
            assert res.status_code == 401
