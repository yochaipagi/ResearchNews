#!/usr/bin/env python3
"""
Test suite for SQLAlchemy models
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Base, Paper, UserAccount, UserSaved, DigestFrequency


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Create a database session for testing"""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


class TestPaperModel:
    """Test Paper model"""
    
    def test_create_paper(self, db_session):
        """Test creating a paper"""
        paper = Paper(
            arxiv_id="2024.0001v1",
            title="Test Paper Title",
            authors="Author One, Author Two",
            abstract="This is a test abstract for our paper.",
            category="cs.AI",
            published_at=datetime.utcnow()
        )
        
        db_session.add(paper)
        db_session.commit()
        
        assert paper.id is not None
        assert paper.arxiv_id == "2024.0001v1"
        assert paper.title == "Test Paper Title"
        assert paper.fetched_at is not None
    
    def test_paper_with_summary(self, db_session):
        """Test paper with AI-generated summary"""
        paper = Paper(
            arxiv_id="2024.0002v1",
            title="Another Test Paper",
            authors="Jane Doe, John Smith",
            abstract="Abstract content here.",
            summary="Short AI-generated summary.",
            category="cs.LG",
            published_at=datetime.utcnow()
        )
        
        db_session.add(paper)
        db_session.commit()
        
        assert paper.summary == "Short AI-generated summary."
    
    def test_paper_embedding(self, db_session):
        """Test paper with vector embedding"""
        # Note: pgvector might not work with SQLite, so we'll test basic functionality
        paper = Paper(
            arxiv_id="2024.0003v1",
            title="Paper with Embedding",
            authors="AI Researcher",
            abstract="Abstract with embedding.",
            category="cs.CV"
        )
        
        db_session.add(paper)
        db_session.commit()
        
        # Test that embedding field exists (will be None in SQLite)
        assert hasattr(paper, 'embedding')
    
    def test_paper_repr(self, db_session):
        """Test paper string representation"""
        paper = Paper(
            arxiv_id="2024.0004v1",
            title="Very Long Title That Should Be Truncated For Display",
            authors="Test Author",
            abstract="Test abstract.",
            category="cs.AI"
        )
        
        db_session.add(paper)
        db_session.commit()
        
        repr_str = repr(paper)
        assert "2024.0004v1" in repr_str
        assert "Very Long Title That Should Be" in repr_str


class TestUserAccountModel:
    """Test UserAccount model"""
    
    def test_create_user(self, db_session):
        """Test creating a user account"""
        user = UserAccount(
            email="test@example.com",
            name="Test User",
            categories=["cs.AI", "cs.LG"],
            frequency=DigestFrequency.DAILY
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.categories == ["cs.AI", "cs.LG"]
        assert user.frequency == DigestFrequency.DAILY
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_digest_frequencies(self, db_session):
        """Test different digest frequencies"""
        users = [
            UserAccount(email="daily@test.com", categories=["cs.AI"], frequency=DigestFrequency.DAILY),
            UserAccount(email="weekly@test.com", categories=["cs.LG"], frequency=DigestFrequency.WEEKLY),
            UserAccount(email="monthly@test.com", categories=["cs.CV"], frequency=DigestFrequency.MONTHLY)
        ]
        
        for user in users:
            db_session.add(user)
        db_session.commit()
        
        daily_user = db_session.query(UserAccount).filter_by(email="daily@test.com").first()
        weekly_user = db_session.query(UserAccount).filter_by(email="weekly@test.com").first()
        monthly_user = db_session.query(UserAccount).filter_by(email="monthly@test.com").first()
        
        assert daily_user.frequency == DigestFrequency.DAILY
        assert weekly_user.frequency == DigestFrequency.WEEKLY
        assert monthly_user.frequency == DigestFrequency.MONTHLY
    
    def test_user_next_digest_time(self, db_session):
        """Test next digest timestamp"""
        future_time = datetime.utcnow() + timedelta(hours=24)
        user = UserAccount(
            email="scheduled@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.DAILY,
            next_digest_at=future_time
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.next_digest_at == future_time
    
    def test_user_inactive(self, db_session):
        """Test inactive user"""
        user = UserAccount(
            email="inactive@test.com",
            categories=["cs.AI"],
            is_active=False
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.is_active is False
    
    def test_user_repr(self, db_session):
        """Test user string representation"""
        user = UserAccount(
            email="repr@test.com",
            categories=["cs.AI"]
        )
        
        db_session.add(user)
        db_session.commit()
        
        repr_str = repr(user)
        assert "repr@test.com" in repr_str


class TestUserSavedModel:
    """Test UserSaved model (many-to-many relationship)"""
    
    def test_save_paper(self, db_session):
        """Test user saving a paper"""
        # Create user and paper
        user = UserAccount(
            email="saver@test.com",
            categories=["cs.AI"]
        )
        paper = Paper(
            arxiv_id="2024.0005v1",
            title="Saved Paper",
            authors="Author",
            abstract="Abstract",
            category="cs.AI"
        )
        
        db_session.add(user)
        db_session.add(paper)
        db_session.commit()
        
        # Create saved relationship
        saved = UserSaved(
            user_id=user.id,
            paper_id=paper.id
        )
        
        db_session.add(saved)
        db_session.commit()
        
        assert saved.user_id == user.id
        assert saved.paper_id == paper.id
        assert saved.saved_at is not None
    
    def test_user_saved_relationships(self, db_session):
        """Test user-paper relationships"""
        # Create user and papers
        user = UserAccount(email="relations@test.com", categories=["cs.AI"])
        paper1 = Paper(arxiv_id="2024.0006v1", title="Paper 1", authors="A", abstract="A", category="cs.AI")
        paper2 = Paper(arxiv_id="2024.0007v1", title="Paper 2", authors="B", abstract="B", category="cs.AI")
        
        db_session.add_all([user, paper1, paper2])
        db_session.commit()
        
        # Save both papers
        saved1 = UserSaved(user_id=user.id, paper_id=paper1.id)
        saved2 = UserSaved(user_id=user.id, paper_id=paper2.id)
        
        db_session.add_all([saved1, saved2])
        db_session.commit()
        
        # Test relationships
        user_saved_papers = db_session.query(UserSaved).filter_by(user_id=user.id).all()
        assert len(user_saved_papers) == 2
        
        # Test accessing related objects through relationships
        user_refresh = db_session.query(UserAccount).filter_by(id=user.id).first()
        assert len(user_refresh.saved_papers) == 2
    
    def test_user_saved_repr(self, db_session):
        """Test UserSaved string representation"""
        user = UserAccount(email="saved_repr@test.com", categories=["cs.AI"])
        paper = Paper(arxiv_id="2024.0008v1", title="Repr Paper", authors="A", abstract="A", category="cs.AI")
        
        db_session.add_all([user, paper])
        db_session.commit()
        
        saved = UserSaved(user_id=user.id, paper_id=paper.id)
        db_session.add(saved)
        db_session.commit()
        
        repr_str = repr(saved)
        assert str(user.id) in repr_str
        assert str(paper.id) in repr_str


class TestDigestFrequencyEnum:
    """Test DigestFrequency enum"""
    
    def test_enum_values(self):
        """Test enum values"""
        assert DigestFrequency.DAILY == "DAILY"
        assert DigestFrequency.WEEKLY == "WEEKLY"
        assert DigestFrequency.MONTHLY == "MONTHLY"
    
    def test_enum_in_model(self, db_session):
        """Test enum usage in model"""
        user = UserAccount(
            email="enum@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.WEEKLY
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify enum value is stored correctly
        saved_user = db_session.query(UserAccount).filter_by(email="enum@test.com").first()
        assert saved_user.frequency == DigestFrequency.WEEKLY
        assert saved_user.frequency.value == "WEEKLY"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])