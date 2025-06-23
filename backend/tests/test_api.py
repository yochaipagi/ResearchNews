#!/usr/bin/env python3
"""
Test suite for FastAPI endpoints
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.api import app, get_current_user
from app.database import get_db
from app.models import Base, UserAccount, Paper, DigestFrequency


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_research_feed.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def create_test_user():
    """Create a test user for authentication"""
    return UserAccount(
        id=1,
        email="test@example.com",
        name="Test User",
        categories=["cs.AI", "cs.LG"],
        frequency=DigestFrequency.DAILY,
        is_active=True
    )

def override_get_current_user():
    """Mock current user for testing"""
    return create_test_user()

# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAPI:
    """Test class for API endpoints"""
    
    def test_root_endpoint(self, setup_database):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Research Digest API is running"}
    
    def test_register_user(self, setup_database):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "categories": ["cs.AI", "cs.CL"],
            "frequency": "DAILY"
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["categories"] == user_data["categories"]
    
    def test_register_existing_user(self, setup_database):
        """Test registering existing user (should update)"""
        user_data = {
            "email": "test@example.com",
            "name": "Updated User",
            "categories": ["cs.CV", "cs.RO"],
            "frequency": "WEEKLY"
        }
        response = client.post("/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
    
    def test_get_profile(self, setup_database):
        """Test get user profile"""
        response = client.get("/profile", headers={"authorization": "Bearer test@example.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
    
    def test_update_profile(self, setup_database):
        """Test update user profile"""
        update_data = {
            "name": "Updated Test User",
            "categories": ["cs.AI", "cs.ML", "cs.CV"]
        }
        response = client.put("/profile", json=update_data, headers={"authorization": "Bearer test@example.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["categories"] == update_data["categories"]
    
    def test_get_categories(self, setup_database):
        """Test get arXiv categories"""
        response = client.get("/categories")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert "cs.AI" in categories
        assert "cs.LG" in categories
    
    def test_trigger_fetch(self, setup_database):
        """Test trigger paper fetch"""
        with patch('app.api.fetch_papers') as mock_fetch:
            mock_fetch.delay.return_value = Mock()
            response = client.post("/trigger/fetch")
            assert response.status_code == 200
            assert "Paper fetch task triggered" in response.json()["message"]
            mock_fetch.delay.assert_called_once()
    
    def test_trigger_summarize(self, setup_database):
        """Test trigger summarization"""
        with patch('app.api.process_summaries') as mock_summarize:
            mock_summarize.delay.return_value = Mock()
            response = client.post("/trigger/summarize", params={"limit": 5})
            assert response.status_code == 200
            assert "Summary processing task triggered for 5 papers" in response.json()["message"]
            mock_summarize.delay.assert_called_once_with(5)
    
    def test_unsubscribe_invalid_token(self, setup_database):
        """Test unsubscribe with invalid token"""
        response = client.get("/unsubscribe", params={"token": "invalid_token"})
        assert response.status_code == 400
        assert "Invalid token" in response.json()["detail"]
    
    def test_unauthorized_access(self, setup_database):
        """Test unauthorized access to protected endpoints"""
        # Remove the override temporarily
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        
        response = client.get("/profile")
        assert response.status_code == 401
        
        # Restore override
        app.dependency_overrides[get_current_user] = override_get_current_user
    
    def test_admin_endpoints_access(self, setup_database):
        """Test admin endpoint access"""
        with patch('app.api.settings') as mock_settings:
            mock_settings.ADMIN_EMAILS = ["test@example.com"]
            
            response = client.get("/admin/users", headers={"authorization": "Bearer test@example.com"})
            assert response.status_code == 200
            
            response = client.get("/admin/stats", headers={"authorization": "Bearer test@example.com"})
            assert response.status_code == 200
    
    def test_admin_endpoints_forbidden(self, setup_database):
        """Test admin endpoint access for non-admin user"""
        with patch('app.api.settings') as mock_settings:
            mock_settings.ADMIN_EMAILS = ["admin@example.com"]  # Different email
            
            response = client.get("/admin/users", headers={"authorization": "Bearer test@example.com"})
            assert response.status_code == 403
            assert "Forbidden" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])