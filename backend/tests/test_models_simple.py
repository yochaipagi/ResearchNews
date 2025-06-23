#!/usr/bin/env python3
"""
Simplified test suite for models - using basic types compatible with SQLite
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, BigInteger, Text, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import DigestFrequency

# Create simplified models for testing
Base = declarative_base()

class SimplePaper(Base):
    __tablename__ = "simple_paper"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    arxiv_id = Column(String, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text)
    abstract = Column(Text)
    summary = Column(Text)
    category = Column(String)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)

class SimpleUserAccount(Base):
    __tablename__ = "simple_user_account"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    categories = Column(String)  # JSON string instead of ARRAY
    frequency = Column(SQLEnum(DigestFrequency), default=DigestFrequency.DAILY)
    next_digest_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_simple_models.db"
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


class TestSimplePaperModel:
    """Test simplified Paper model"""
    
    def test_create_paper(self, db_session):
        """Test creating a paper"""
        paper = SimplePaper(
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
        paper = SimplePaper(
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
    
    def test_unique_arxiv_id(self, db_session):
        """Test arxiv_id uniqueness constraint"""
        paper1 = SimplePaper(
            arxiv_id="2024.duplicate.v1",
            title="First Paper",
            authors="Author 1",
            abstract="Abstract 1",
            category="cs.AI"
        )
        paper2 = SimplePaper(
            arxiv_id="2024.duplicate.v1",  # Same ID
            title="Second Paper",
            authors="Author 2",
            abstract="Abstract 2",
            category="cs.LG"
        )
        
        db_session.add(paper1)
        db_session.commit()
        
        db_session.add(paper2)
        
        # Should raise integrity error for duplicate arxiv_id
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            db_session.commit()


class TestSimpleUserAccountModel:
    """Test simplified UserAccount model"""
    
    def test_create_user(self, db_session):
        """Test creating a user account"""
        user = SimpleUserAccount(
            email="test@example.com",
            name="Test User",
            categories='["cs.AI", "cs.LG"]',  # JSON string
            frequency=DigestFrequency.DAILY
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.categories == '["cs.AI", "cs.LG"]'
        assert user.frequency == DigestFrequency.DAILY
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_digest_frequencies(self, db_session):
        """Test different digest frequencies"""
        users = [
            SimpleUserAccount(email="daily@test.com", categories='["cs.AI"]', frequency=DigestFrequency.DAILY),
            SimpleUserAccount(email="weekly@test.com", categories='["cs.LG"]', frequency=DigestFrequency.WEEKLY),
            SimpleUserAccount(email="monthly@test.com", categories='["cs.CV"]', frequency=DigestFrequency.MONTHLY)
        ]
        
        for user in users:
            db_session.add(user)
        db_session.commit()
        
        daily_user = db_session.query(SimpleUserAccount).filter_by(email="daily@test.com").first()
        weekly_user = db_session.query(SimpleUserAccount).filter_by(email="weekly@test.com").first()
        monthly_user = db_session.query(SimpleUserAccount).filter_by(email="monthly@test.com").first()
        
        assert daily_user.frequency == DigestFrequency.DAILY
        assert weekly_user.frequency == DigestFrequency.WEEKLY
        assert monthly_user.frequency == DigestFrequency.MONTHLY
    
    def test_user_defaults(self, db_session):
        """Test user default values"""
        user = SimpleUserAccount(
            email="defaults@test.com",
            categories='["cs.AI"]'
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Check defaults
        assert user.frequency == DigestFrequency.DAILY
        assert user.is_active is True
        assert user.created_at is not None
        assert user.next_digest_at is None  # No default
        assert user.name is None  # Optional field
    
    def test_unique_email(self, db_session):
        """Test email uniqueness constraint"""
        user1 = SimpleUserAccount(email="duplicate@test.com", categories='["cs.AI"]')
        user2 = SimpleUserAccount(email="duplicate@test.com", categories='["cs.LG"]')
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        
        # Should raise integrity error for duplicate email
        with pytest.raises(Exception):
            db_session.commit()


class TestDigestFrequencyEnum:
    """Test DigestFrequency enum"""
    
    def test_enum_values(self):
        """Test enum values"""
        assert DigestFrequency.DAILY == "DAILY"
        assert DigestFrequency.WEEKLY == "WEEKLY"
        assert DigestFrequency.MONTHLY == "MONTHLY"
    
    def test_enum_in_model(self, db_session):
        """Test enum usage in model"""
        user = SimpleUserAccount(
            email="enum@test.com",
            categories='["cs.AI"]',
            frequency=DigestFrequency.WEEKLY
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify enum value is stored correctly
        saved_user = db_session.query(SimpleUserAccount).filter_by(email="enum@test.com").first()
        assert saved_user.frequency == DigestFrequency.WEEKLY
        assert saved_user.frequency.value == "WEEKLY"


class TestDatabaseIntegration:
    """Test database operations"""
    
    def test_query_papers_by_category(self, db_session):
        """Test querying papers by category"""
        papers = [
            SimplePaper(arxiv_id="2024.ai.1", title="AI Paper 1", category="cs.AI", authors="A", abstract="A"),
            SimplePaper(arxiv_id="2024.ai.2", title="AI Paper 2", category="cs.AI", authors="B", abstract="B"),
            SimplePaper(arxiv_id="2024.cv.1", title="CV Paper 1", category="cs.CV", authors="C", abstract="C"),
        ]
        
        for paper in papers:
            db_session.add(paper)
        db_session.commit()
        
        # Query AI papers
        ai_papers = db_session.query(SimplePaper).filter_by(category="cs.AI").all()
        assert len(ai_papers) == 2
        
        # Query CV papers
        cv_papers = db_session.query(SimplePaper).filter_by(category="cs.CV").all()
        assert len(cv_papers) == 1
    
    def test_query_active_users(self, db_session):
        """Test querying active users"""
        users = [
            SimpleUserAccount(email="active1@test.com", categories='["cs.AI"]', is_active=True),
            SimpleUserAccount(email="active2@test.com", categories='["cs.LG"]', is_active=True),
            SimpleUserAccount(email="inactive@test.com", categories='["cs.CV"]', is_active=False),
        ]
        
        for user in users:
            db_session.add(user)
        db_session.commit()
        
        # Query active users
        active_users = db_session.query(SimpleUserAccount).filter_by(is_active=True).all()
        assert len(active_users) == 2
        
        # Query inactive users
        inactive_users = db_session.query(SimpleUserAccount).filter_by(is_active=False).all()
        assert len(inactive_users) == 1
    
    def test_datetime_handling(self, db_session):
        """Test datetime field handling"""
        now = datetime.utcnow()
        future = now + timedelta(days=1)
        
        user = SimpleUserAccount(
            email="datetime@test.com",
            categories='["cs.AI"]',
            next_digest_at=future
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Verify datetime fields
        saved_user = db_session.query(SimpleUserAccount).filter_by(email="datetime@test.com").first()
        assert saved_user.created_at is not None
        assert saved_user.next_digest_at == future
        assert saved_user.created_at <= now + timedelta(seconds=1)  # Allow small time difference


if __name__ == "__main__":
    pytest.main([__file__, "-v"])