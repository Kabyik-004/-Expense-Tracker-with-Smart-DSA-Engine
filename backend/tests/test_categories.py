"""Tests for category endpoints."""

import pytest

from app import create_app, db
from app.config import TestingConfig
from app.models.user import User
from app.models.category import Category


class TestCategoryEndpoints:

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
        user = User(username="catuser", email="cat@example.com", full_name="Cat User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        login_res = app.test_client().post("/api/auth/login", json={
            "login": "catuser", "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def test_list_categories_empty(self, client, auth_headers):
        res = client.get("/api/categories/", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["categories"] == []

    def test_list_categories_with_data(self, client, auth_headers, app):
        with app.app_context():
            user = User.query.filter_by(username="catuser").first()
            cats = [
                Category(user_id=user.id, name="Food", icon="🍔", color="#ff0000"),
                Category(user_id=user.id, name="Transport", icon="🚗", color="#00ff00"),
            ]
            db.session.add_all(cats)
            db.session.commit()
        res = client.get("/api/categories/", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["data"]["categories"]) == 2
        names = [c["name"] for c in data["data"]["categories"]]
        assert "Food" in names
        assert "Transport" in names

    def test_categories_ordered_by_name(self, client, auth_headers, app):
        with app.app_context():
            user = User.query.filter_by(username="catuser").first()
            cats = [
                Category(user_id=user.id, name="Zoo", icon="🦁"),
                Category(user_id=user.id, name="Apple", icon="🍎"),
            ]
            db.session.add_all(cats)
            db.session.commit()
        res = client.get("/api/categories/", headers=auth_headers)
        names = [c["name"] for c in res.get_json()["data"]["categories"]]
        assert names == ["Apple", "Zoo"]

    def test_categories_user_isolation(self, client, auth_headers, app):
        with app.app_context():
            other_user = User(username="other", email="other@example.com")
            other_user.set_password("TestPass1")
            db.session.add(other_user)
            db.session.commit()
            cat = Category(user_id=other_user.id, name="Other Cat")
            db.session.add(cat)
            db.session.commit()
        res = client.get("/api/categories/", headers=auth_headers)
        assert len(res.get_json()["data"]["categories"]) == 0

    def test_categories_requires_jwt(self, client):
        res = client.get("/api/categories/")
        assert res.status_code == 401
