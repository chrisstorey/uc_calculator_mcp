"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Provide test client."""
    return TestClient(app)


@pytest.fixture
def sample_user():
    """Provide sample user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPassword123",
    }


@pytest.fixture
def sample_item():
    """Provide sample item data."""
    return {
        "title": "Test Item",
        "description": "A test item",
        "price": 9.99,
    }
