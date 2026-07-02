"""
Analytics tests — API endpoints for spending analysis.

Covers:
- Overview: totals, balance, extremes
- Categories: most used, top 5, distribution
- Time series: daily, weekly, monthly breakdown
- Dashboard: comprehensive view
"""

import pytest
from datetime import date, timedelta

from app import create_app, db
from app.config import TestingConfig
from app.models.user import User
from app.models.expense import Expense
from app.models.income import Income
from app.models.category import Category


class TestAnalyticsEndpoints:
    """Test analytics API endpoints."""
    
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
        user = User(username="analyticuser", email="analytics@example.com", full_name="Analytics User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        
        login_res = app.test_client().post("/api/auth/login", json={
            "login": "analyticuser",
            "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    
    @pytest.fixture
    def user(self, app):
        return User.query.filter_by(username="analyticuser").first()
    
    @pytest.fixture
    def sample_data(self, app, user):
        """Create sample expenses and income for testing."""
        with app.app_context():
            # Create categories
            food_cat = Category(user_id=user.id, name="Food", icon="🍔")
            transport_cat = Category(user_id=user.id, name="Transport", icon="🚗")
            entertainment_cat = Category(user_id=user.id, name="Entertainment", icon="🎮")
            db.session.add_all([food_cat, transport_cat, entertainment_cat])
            db.session.commit()
            
            # Create expenses spread over multiple days
            expenses = [
                Expense(user_id=user.id, title="Coffee", amount=5.00, category_id=food_cat.id, date=date(2026, 7, 1)),
                Expense(user_id=user.id, title="Lunch", amount=15.00, category_id=food_cat.id, date=date(2026, 7, 1)),
                Expense(user_id=user.id, title="Dinner", amount=25.00, category_id=food_cat.id, date=date(2026, 7, 2)),
                Expense(user_id=user.id, title="Taxi", amount=20.00, category_id=transport_cat.id, date=date(2026, 7, 3)),
                Expense(user_id=user.id, title="Movie", amount=12.00, category_id=entertainment_cat.id, date=date(2026, 7, 4)),
                Expense(user_id=user.id, title="Bus", amount=2.50, category_id=transport_cat.id, date=date(2026, 7, 5)),
            ]
            db.session.add_all(expenses)
            
            # Create income
            income_entries = [
                Income(user_id=user.id, source="Salary", amount=3000.00, date=date(2026, 7, 1)),
                Income(user_id=user.id, source="Bonus", amount=500.00, date=date(2026, 7, 15)),
            ]
            db.session.add_all(income_entries)
            db.session.commit()
            
            return {
                "expenses": expenses,
                "income": income_entries,
                "categories": {
                    "food": food_cat,
                    "transport": transport_cat,
                    "entertainment": entertainment_cat
                }
            }
    
    def test_analytics_overview_endpoint(self, client, auth_headers, app, sample_data):
        """GET /api/analytics/overview - Get overview with totals and extremes."""
        response = client.get("/api/analytics/overview", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        overview = data["data"]
        
        # Check totals
        assert overview["total_expense"] == 79.50  # 5+15+25+20+12+2.50
        assert overview["total_income"] == 3500.00  # 3000+500
        assert overview["balance"] == 3420.50  # 3500 - 79.50
        
        # Check extremes
        assert overview["highest_expense"]["amount"] == 25.00  # Dinner
        assert overview["highest_expense"]["title"] == "Dinner"
        
        assert overview["lowest_expense"]["amount"] == 2.50  # Bus
        assert overview["lowest_expense"]["title"] == "Bus"
        
        # Average: 79.50 / 6 = 13.25
        assert overview["average_expense"] == 13.25
    
    def test_analytics_overview_no_data(self, client, auth_headers):
        """Overview with no expenses returns zeros."""
        response = client.get("/api/analytics/overview", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        overview = data["data"]
        
        assert overview["total_expense"] == 0.0
        assert overview["total_income"] == 0.0
        assert overview["balance"] == 0.0
        assert overview["highest_expense"] is None
        assert overview["lowest_expense"] is None
        assert overview["average_expense"] == 0.0
    
    def test_category_analytics_endpoint(self, client, auth_headers, app, sample_data):
        """GET /api/analytics/categories - Get category breakdown."""
        response = client.get("/api/analytics/categories", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        categories = data["data"]
        
        # Check most used category
        most_used = categories["most_used_category"]
        assert most_used["category_name"] == "Food"  # 3 expenses
        assert most_used["count"] == 3
        
        # Check top 5 categories (should be all 3)
        top_5 = categories["top_5_categories"]
        assert len(top_5) == 3
        
        # First should be Food (45.00 total)
        assert top_5[0]["category_name"] == "Food"
        assert top_5[0]["total_amount"] == 45.00
        assert top_5[0]["expense_count"] == 3
        
        # Second should be Transport (22.50 total)
        assert top_5[1]["category_name"] == "Transport"
        assert top_5[1]["total_amount"] == 22.50
        
        # Check distribution
        distribution = categories["category_distribution"]
        assert len(distribution) == 3
        
        # Verify percentages sum to 100
        total_percent = sum(cat["percentage"] for cat in distribution)
        assert total_percent == 100.0
        
        # Food should be ~56.60% (45/79.50)
        assert distribution[0]["percentage"] == pytest.approx(56.60, abs=0.1)
    
    def test_time_series_analytics_endpoint(self, client, auth_headers, app, sample_data):
        """GET /api/analytics/time-series - Get daily, weekly, monthly breakdown."""
        response = client.get("/api/analytics/time-series", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        time_series = data["data"]
        
        # Check daily breakdown
        daily = time_series["daily"]
        assert "2026-07-01" in daily
        assert daily["2026-07-01"]["total"] == 20.00  # Coffee + Lunch
        assert daily["2026-07-01"]["count"] == 2
        
        assert "2026-07-02" in daily
        assert daily["2026-07-02"]["total"] == 25.00  # Dinner
        assert daily["2026-07-02"]["count"] == 1
        
        # Check weekly breakdown (SQLite strftime('%Y-%W') format)
        weekly = time_series["weekly"]
        assert len(weekly) > 0
        week_key = list(weekly.keys())[0]
        assert weekly[week_key]["total"] == 79.50
        assert weekly[week_key]["count"] == 6
        
        # Check monthly breakdown
        monthly = time_series["monthly"]
        assert "2026-07" in monthly
        assert monthly["2026-07"]["total"] == 79.50
        assert monthly["2026-07"]["count"] == 6
    
    def test_dashboard_analytics_endpoint(self, client, auth_headers, app, sample_data):
        """GET /api/analytics/dashboard - Get complete dashboard."""
        response = client.get("/api/analytics/dashboard", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        dashboard = data["data"]
        
        # Check summary section
        assert "summary" in dashboard
        summary = dashboard["summary"]
        assert summary["total_expense"] == 79.50
        assert summary["total_income"] == 3500.00
        assert summary["balance"] == 3420.50
        
        # Check extremes section
        assert "extremes" in dashboard
        extremes = dashboard["extremes"]
        assert extremes["highest_expense"]["amount"] == 25.00
        assert extremes["lowest_expense"]["amount"] == 2.50
        assert extremes["average_expense"] == 13.25
        
        # Check categories section
        assert "categories" in dashboard
        categories = dashboard["categories"]
        assert categories["most_used"] is not None
        assert len(categories["top_5"]) > 0
        assert len(categories["distribution"]) > 0
        
        # Check time_series section
        assert "time_series" in dashboard
        time_series = dashboard["time_series"]
        assert "daily" in time_series
        assert "weekly" in time_series
        assert "monthly" in time_series
    
    def test_analytics_requires_jwt(self, client):
        """Analytics endpoints require JWT authentication."""
        endpoints = [
            "/api/analytics/overview",
            "/api/analytics/categories",
            "/api/analytics/time-series",
            "/api/analytics/dashboard",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401  # Unauthorized


class TestAnalyticsCalculations:
    """Unit tests for analytics calculations."""
    
    @pytest.fixture
    def app(self):
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    def test_total_expenses_calculation(self, app):
        """Verify total expense calculation."""
        from app.controllers.analytics_controller import get_total_expenses
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create expenses
            expenses = [
                Expense(user_id=user.id, title="E1", amount=10.00, date=date.today()),
                Expense(user_id=user.id, title="E2", amount=20.00, date=date.today()),
                Expense(user_id=user.id, title="E3", amount=15.50, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            total = get_total_expenses(user.id)
            assert total == 45.50
    
    def test_balance_calculation(self, app):
        """Verify balance: income - expense."""
        from app.controllers.analytics_controller import get_balance
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Add income
            income = Income(user_id=user.id, source="Salary", amount=1000.00, date=date.today())
            db.session.add(income)
            
            # Add expense
            expense = Expense(user_id=user.id, title="Expense", amount=300.00, date=date.today())
            db.session.add(expense)
            db.session.commit()
            
            balance = get_balance(user.id)
            assert balance == 700.00  # 1000 - 300
    
    def test_average_expense_calculation(self, app):
        """Verify average expense calculation."""
        from app.controllers.analytics_controller import get_average_expense
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create expenses
            expenses = [
                Expense(user_id=user.id, title="E1", amount=10.00, date=date.today()),
                Expense(user_id=user.id, title="E2", amount=20.00, date=date.today()),
                Expense(user_id=user.id, title="E3", amount=30.00, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            avg = get_average_expense(user.id)
            assert avg == 20.00  # (10 + 20 + 30) / 3
    
    def test_category_distribution_percentages(self, app):
        """Verify category distribution percentages are correct."""
        from app.controllers.analytics_controller import get_category_distribution
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create categories
            cat1 = Category(user_id=user.id, name="Cat1", icon="1")
            cat2 = Category(user_id=user.id, name="Cat2", icon="2")
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            # Create expenses: 50 in cat1, 50 in cat2 (each 50%)
            expenses = [
                Expense(user_id=user.id, title="E1", amount=50.00, category_id=cat1.id, date=date.today()),
                Expense(user_id=user.id, title="E2", amount=50.00, category_id=cat2.id, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            distribution = get_category_distribution(user.id)
            assert len(distribution) == 2
            
            # Each should be 50%
            assert distribution[0]["percentage"] == 50.0
            assert distribution[1]["percentage"] == 50.0
    
    def test_monthly_grouping(self, app):
        """Verify monthly expense grouping."""
        from app.controllers.analytics_controller import get_monthly_expenses
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create expenses across two months
            expenses = [
                Expense(user_id=user.id, title="E1", amount=100.00, date=date(2026, 6, 15)),
                Expense(user_id=user.id, title="E2", amount=50.00, date=date(2026, 6, 20)),
                Expense(user_id=user.id, title="E3", amount=75.00, date=date(2026, 7, 1)),
                Expense(user_id=user.id, title="E4", amount=25.00, date=date(2026, 7, 15)),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            monthly = get_monthly_expenses(user.id)
            
            # Should have two months
            assert "2026-06" in monthly
            assert monthly["2026-06"]["total"] == 150.00
            assert monthly["2026-06"]["count"] == 2
            
            assert "2026-07" in monthly
            assert monthly["2026-07"]["total"] == 100.00
            assert monthly["2026-07"]["count"] == 2
    
    def test_highest_and_lowest_expense(self, app):
        """Verify highest and lowest expense detection."""
        from app.controllers.analytics_controller import get_highest_expense, get_lowest_expense
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create expenses
            expenses = [
                Expense(user_id=user.id, title="Cheap", amount=1.00, date=date.today()),
                Expense(user_id=user.id, title="Medium", amount=50.00, date=date.today()),
                Expense(user_id=user.id, title="Expensive", amount=100.00, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            highest = get_highest_expense(user.id)
            assert highest["title"] == "Expensive"
            assert highest["amount"] == 100.00
            
            lowest = get_lowest_expense(user.id)
            assert lowest["title"] == "Cheap"
            assert lowest["amount"] == 1.00
    
    def test_most_used_category(self, app):
        """Verify most used category detection."""
        from app.controllers.analytics_controller import get_most_used_category
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create categories
            cat1 = Category(user_id=user.id, name="Food", icon="🍔")
            cat2 = Category(user_id=user.id, name="Transport", icon="🚗")
            db.session.add_all([cat1, cat2])
            db.session.commit()
            
            # Create expenses: 3 in cat1, 1 in cat2
            expenses = [
                Expense(user_id=user.id, title="E1", amount=10.00, category_id=cat1.id, date=date.today()),
                Expense(user_id=user.id, title="E2", amount=10.00, category_id=cat1.id, date=date.today()),
                Expense(user_id=user.id, title="E3", amount=10.00, category_id=cat1.id, date=date.today()),
                Expense(user_id=user.id, title="E4", amount=10.00, category_id=cat2.id, date=date.today()),
            ]
            db.session.add_all(expenses)
            db.session.commit()
            
            most_used = get_most_used_category(user.id)
            assert most_used["category_name"] == "Food"
            assert most_used["count"] == 3
    
    def test_top_5_categories(self, app):
        """Verify top 5 categories by total amount."""
        from app.controllers.analytics_controller import get_top_5_categories
        
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            
            # Create 6 categories
            categories = []
            for i in range(6):
                cat = Category(user_id=user.id, name=f"Cat{i}", icon=str(i))
                categories.append(cat)
            db.session.add_all(categories)
            db.session.commit()
            
            # Create expenses: varying amounts
            # Cat0: 100, Cat1: 90, Cat2: 80, Cat3: 70, Cat4: 60, Cat5: 50
            for i, cat in enumerate(categories):
                amount = 100 - (i * 10)
                exp = Expense(
                    user_id=user.id,
                    title=f"E{i}",
                    amount=float(amount),
                    category_id=cat.id,
                    date=date.today()
                )
                db.session.add(exp)
            db.session.commit()
            
            top_5 = get_top_5_categories(user.id)
            
            # Should have exactly 5
            assert len(top_5) == 5
            
            # Should be in descending order
            assert top_5[0]["total_amount"] == 100.0
            assert top_5[1]["total_amount"] == 90.0
            assert top_5[2]["total_amount"] == 80.0
            assert top_5[3]["total_amount"] == 70.0
            assert top_5[4]["total_amount"] == 60.0
