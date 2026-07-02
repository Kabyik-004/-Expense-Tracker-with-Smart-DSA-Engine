"""Tests for Stack data structure and undo/redo functionality."""

import pytest
from app import create_app, db
from app.config import TestingConfig
from app.controllers.expense_controller import (
    reset_expense_summaries,
    _get_user_undo_stack,
    clear_undo_stack,
)
from app.models.user import User
from app.services.stack import Stack


class TestStackDataStructure:
    """Unit tests for the custom Stack implementation."""

    def test_stack_push_pop(self):
        """Test basic push and pop operations."""
        stack = Stack(max_size=5)
        stack.push("A")
        stack.push("B")
        stack.push("C")
        
        assert stack.pop() == "C"
        assert stack.pop() == "B"
        assert stack.pop() == "A"
        assert stack.pop() is None

    def test_stack_peek(self):
        """Test peek without removing element."""
        stack = Stack(max_size=5)
        stack.push("X")
        stack.push("Y")
        
        assert stack.peek() == "Y"
        assert stack.peek() == "Y"  # Still there
        assert stack.size() == 2

    def test_stack_size(self):
        """Test size tracking."""
        stack = Stack(max_size=5)
        assert stack.size() == 0
        
        stack.push("A")
        assert stack.size() == 1
        
        stack.push("B")
        assert stack.size() == 2
        
        stack.pop()
        assert stack.size() == 1

    def test_stack_is_empty(self):
        """Test empty check."""
        stack = Stack(max_size=5)
        assert stack.is_empty() is True
        
        stack.push("A")
        assert stack.is_empty() is False
        
        stack.pop()
        assert stack.is_empty() is True

    def test_stack_is_full(self):
        """Test full check."""
        stack = Stack(max_size=3)
        assert stack.is_full() is False
        
        stack.push("A")
        stack.push("B")
        assert stack.is_full() is False
        
        stack.push("C")
        assert stack.is_full() is True

    def test_stack_max_size_enforcement(self):
        """Test that max_size is enforced by removing oldest items."""
        stack = Stack(max_size=3)
        
        stack.push("A")  # Stack: [A]
        stack.push("B")  # Stack: [A, B]
        stack.push("C")  # Stack: [A, B, C]
        assert stack.size() == 3
        
        stack.push("D")  # Stack: [B, C, D] - A removed (oldest)
        assert stack.size() == 3
        assert stack.pop() == "D"
        assert stack.pop() == "C"
        assert stack.pop() == "B"
        assert stack.pop() is None  # A is gone

    def test_stack_lifo_order(self):
        """Test Last-In-First-Out behavior."""
        stack = Stack(max_size=10)
        items = [1, 2, 3, 4, 5]
        
        for item in items:
            stack.push(item)
        
        # Should pop in reverse order
        assert stack.pop() == 5
        assert stack.pop() == 4
        assert stack.pop() == 3
        assert stack.pop() == 2
        assert stack.pop() == 1

    def test_stack_clear(self):
        """Test clearing the stack."""
        stack = Stack(max_size=5)
        stack.push("A")
        stack.push("B")
        stack.push("C")
        
        assert stack.size() == 3
        stack.clear()
        assert stack.size() == 0
        assert stack.is_empty() is True

    def test_stack_to_list(self):
        """Test converting stack to list."""
        stack = Stack(max_size=5)
        stack.push("A")
        stack.push("B")
        stack.push("C")
        
        items = stack.to_list()
        assert items == ["A", "B", "C"]
        
        # Original stack unchanged
        assert stack.size() == 3

    def test_stack_with_dict_objects(self):
        """Test stack with complex objects."""
        stack = Stack(max_size=10)
        
        obj1 = {"id": 1, "name": "Item 1"}
        obj2 = {"id": 2, "name": "Item 2"}
        
        stack.push(obj1)
        stack.push(obj2)
        
        assert stack.pop() == obj2
        assert stack.pop() == obj1

    def test_stack_lifo_explanation(self):
        """Test that stack documentation exists."""
        assert callable(Stack)
        assert Stack.__doc__ is not None
        assert "LIFO" in Stack.__doc__ or "Last-In" in Stack.__doc__


class TestUndoFunctionality:
    """Integration tests for undo/redo functionality."""

    @pytest.fixture
    def app(self):
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            reset_expense_summaries()
            # Clear undo stacks for test isolation
            from app.controllers import expense_controller
            expense_controller._undo_stacks.clear()
            yield app
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, app):
        user = User(username="undouser", email="undo@example.com", full_name="Undo User")
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()

        login_res = app.test_client().post(
            "/api/auth/login",
            json={"login": "undouser", "password": "TestPass1"},
        )
        access_token = login_res.get_json()["data"]["access_token"]
        return {"Authorization": f"Bearer {access_token}"}

    def test_undo_create_expense(self, client, auth_headers):
        """Test undoing expense creation."""
        # Create an expense
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Test Expense", "amount": 50.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        assert create_res.status_code == 201
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        # Verify expense exists
        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert get_res.status_code == 200

        # Undo the creation
        undo_res = client.post("/api/expenses/undo", headers=auth_headers)
        assert undo_res.status_code == 200
        assert "Undo" in undo_res.get_json()["message"]

        # Verify expense is now deleted
        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert get_res.status_code == 404

    def test_undo_delete_expense(self, client, auth_headers):
        """Test undoing expense deletion."""
        # Create an expense
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Test Expense", "amount": 50.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        # Delete the expense
        delete_res = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert delete_res.status_code == 200

        # Verify expense is deleted
        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert get_res.status_code == 404

        # Undo the deletion (skip the create undo first)
        undo_res = client.post("/api/expenses/undo", headers=auth_headers)
        assert undo_res.status_code == 200

        # Verify expense is restored
        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert get_res.status_code == 200

    def test_undo_update_expense(self, client, auth_headers):
        """Test undoing expense update."""
        # Create an expense
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Original", "amount": 50.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        # Update the expense
        update_res = client.put(
            f"/api/expenses/{expense_id}",
            json={"title": "Modified", "amount": 100.0},
            headers=auth_headers,
        )
        assert update_res.status_code == 200
        assert update_res.get_json()["data"]["expense"]["title"] == "Modified"
        assert update_res.get_json()["data"]["expense"]["amount"] == 100.0

        # Undo the update
        undo_res = client.post("/api/expenses/undo", headers=auth_headers)
        assert undo_res.status_code == 200

        # Verify values are restored
        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        expense = get_res.get_json()["data"]["expense"]
        assert expense["title"] == "Original"
        assert expense["amount"] == 50.0

    def test_undo_stack_status(self, client, auth_headers):
        """Test getting undo stack status."""
        # Check initial empty status
        status_res = client.get("/api/expenses/undo/status", headers=auth_headers)
        assert status_res.status_code == 200
        data = status_res.get_json()["data"]
        assert data["stack_size"] == 0
        assert data["is_empty"] is True
        assert data["max_size"] == 10

        # Create an expense (adds to undo stack)
        client.post(
            "/api/expenses/",
            json={"title": "Test", "amount": 50.0, "date": "2026-07-01"},
            headers=auth_headers,
        )

        # Check status after creation
        status_res = client.get("/api/expenses/undo/status", headers=auth_headers)
        data = status_res.get_json()["data"]
        assert data["stack_size"] == 1
        assert data["is_empty"] is False
        assert data["top_operation"]["action"] == "CREATE"

    def test_undo_stack_max_size_10(self, client, auth_headers):
        """Test that undo stack respects maximum size of 10."""
        # Create 12 expenses to exceed max_size of 10
        expense_ids = []
        for i in range(12):
            create_res = client.post(
                "/api/expenses/",
                json={"title": f"Expense {i}", "amount": 10.0 + i, "date": "2026-07-01"},
                headers=auth_headers,
            )
            expense_ids.append(create_res.get_json()["data"]["expense"]["id"])

        # Check stack status
        status_res = client.get("/api/expenses/undo/status", headers=auth_headers)
        data = status_res.get_json()["data"]
        assert data["stack_size"] == 10  # Max size enforced

        # Undo all 10 operations
        for _ in range(10):
            undo_res = client.post("/api/expenses/undo", headers=auth_headers)
            assert undo_res.status_code == 200

        # Undo again should fail (stack empty)
        undo_res = client.post("/api/expenses/undo", headers=auth_headers)
        assert undo_res.status_code == 400
        assert "No undo history" in undo_res.get_json()["message"]

    def test_clear_undo_stack(self, client, auth_headers):
        """Test clearing the undo stack."""
        # Create an expense
        client.post(
            "/api/expenses/",
            json={"title": "Test", "amount": 50.0, "date": "2026-07-01"},
            headers=auth_headers,
        )

        # Verify stack has item
        status_res = client.get("/api/expenses/undo/status", headers=auth_headers)
        assert status_res.get_json()["data"]["stack_size"] == 1

        # Clear the stack
        clear_res = client.post("/api/expenses/undo/clear", headers=auth_headers)
        assert clear_res.status_code == 200

        # Verify stack is now empty
        status_res = client.get("/api/expenses/undo/status", headers=auth_headers)
        assert status_res.get_json()["data"]["stack_size"] == 0

    def test_multiple_undo_operations(self, client, auth_headers):
        """Test multiple sequential undo operations."""
        # Create 3 expenses
        expense_ids = []
        for i in range(3):
            create_res = client.post(
                "/api/expenses/",
                json={"title": f"Expense {i}", "amount": 10.0 + i, "date": "2026-07-01"},
                headers=auth_headers,
            )
            expense_ids.append(create_res.get_json()["data"]["expense"]["id"])

        # Verify all 3 exist
        list_res = client.get("/api/expenses/", headers=auth_headers)
        assert len(list_res.get_json()["data"]["expenses"]) == 3

        # Undo creation of 3rd expense
        undo_res = client.post("/api/expenses/undo", headers=auth_headers)
        assert undo_res.status_code == 200

        list_res = client.get("/api/expenses/", headers=auth_headers)
        assert len(list_res.get_json()["data"]["expenses"]) == 2

        # Undo creation of 2nd expense
        undo_res = client.post("/api/expenses/undo", headers=auth_headers)
        assert undo_res.status_code == 200

        list_res = client.get("/api/expenses/", headers=auth_headers)
        assert len(list_res.get_json()["data"]["expenses"]) == 1

    def test_undo_with_modified_expense(self, client, auth_headers):
        """Test undo on a create followed by an update."""
        # Create an expense
        create_res = client.post(
            "/api/expenses/",
            json={"title": "Original", "amount": 50.0, "date": "2026-07-01"},
            headers=auth_headers,
        )
        expense_id = create_res.get_json()["data"]["expense"]["id"]

        # Update it
        client.put(
            f"/api/expenses/{expense_id}",
            json={"title": "Modified", "amount": 100.0},
            headers=auth_headers,
        )

        # Undo the update (should restore to "Original", 50.0)
        client.post("/api/expenses/undo", headers=auth_headers)

        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        expense = get_res.get_json()["data"]["expense"]
        assert expense["title"] == "Original"
        assert expense["amount"] == 50.0

        # Undo the create (should delete the expense)
        client.post("/api/expenses/undo", headers=auth_headers)

        get_res = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
        assert get_res.status_code == 404
