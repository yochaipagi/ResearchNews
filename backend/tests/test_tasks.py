#!/usr/bin/env python3
"""
Test suite for Celery tasks
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Base, UserAccount, Paper, DigestFrequency
from app.tasks import (
    fetch_papers,
    process_summaries,
    calculate_next_digest_time,
    check_digest_schedule,
    send_digest_email_task
)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tasks.db"
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


class TestFetchPapersTask:
    """Test fetch_papers Celery task"""
    
    def test_fetch_papers_task(self):
        """Test fetch papers task execution"""
        with patch('app.tasks.asyncio.get_event_loop') as mock_loop:
            mock_event_loop = Mock()
            mock_loop.return_value = mock_event_loop
            
            with patch('app.tasks.ingest_papers_for_categories') as mock_ingest:
                result = fetch_papers()
                
                assert result is True
                mock_event_loop.run_until_complete.assert_called_once()
                mock_ingest.assert_called_once()


class TestProcessSummariesTask:
    """Test process_summaries Celery task"""
    
    def test_process_summaries_task(self):
        """Test process summaries task execution"""
        with patch('app.tasks.asyncio.get_event_loop') as mock_loop:
            mock_event_loop = Mock()
            mock_loop.return_value = mock_event_loop
            
            with patch('app.tasks.process_unsummarized_papers') as mock_process:
                result = process_summaries(limit=5)
                
                assert result is True
                mock_event_loop.run_until_complete.assert_called_once_with(mock_process(5))
    
    def test_process_summaries_default_limit(self):
        """Test process summaries with default limit"""
        with patch('app.tasks.asyncio.get_event_loop') as mock_loop:
            mock_event_loop = Mock()
            mock_loop.return_value = mock_event_loop
            
            with patch('app.tasks.process_unsummarized_papers') as mock_process:
                result = process_summaries()  # No limit specified
                
                assert result is True
                mock_event_loop.run_until_complete.assert_called_once_with(mock_process(10))


class TestCalculateNextDigestTime:
    """Test digest time calculation"""
    
    def test_calculate_next_digest_time_daily(self):
        """Test daily digest time calculation"""
        user = UserAccount(
            email="daily@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.DAILY
        )
        
        next_time = calculate_next_digest_time(user)
        now = datetime.utcnow()
        
        # Should be tomorrow at approximately the same time
        assert next_time.date() == (now.date() + timedelta(days=1))
        assert abs((next_time - now).total_seconds() - 86400) < 3600  # Within 1 hour of 24 hours later
    
    def test_calculate_next_digest_time_weekly(self):
        """Test weekly digest time calculation"""
        user = UserAccount(
            email="weekly@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.WEEKLY
        )
        
        next_time = calculate_next_digest_time(user)
        now = datetime.utcnow()
        
        # Should be next week at approximately the same time
        expected_days = 7
        time_diff = (next_time - now).total_seconds()
        expected_seconds = expected_days * 86400
        
        assert abs(time_diff - expected_seconds) < 3600  # Within 1 hour of 7 days later
    
    def test_calculate_next_digest_time_monthly(self):
        """Test monthly digest time calculation"""
        user = UserAccount(
            email="monthly@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.MONTHLY
        )
        
        next_time = calculate_next_digest_time(user)
        now = datetime.utcnow()
        
        # Should be next month
        if now.month == 12:
            expected_month = 1
            expected_year = now.year + 1
        else:
            expected_month = now.month + 1
            expected_year = now.year
        
        assert next_time.month == expected_month
        assert next_time.year == expected_year
    
    def test_calculate_next_digest_time_end_of_month(self):
        """Test monthly digest calculation for end-of-month dates"""
        # Mock a date at the end of January (31st)
        with patch('app.tasks.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 31, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            user = UserAccount(
                email="monthly@test.com",
                categories=["cs.AI"],
                frequency=DigestFrequency.MONTHLY
            )
            
            next_time = calculate_next_digest_time(user)
            
            # February only has 28/29 days, so should be Feb 28/29
            assert next_time.month == 2
            assert next_time.day <= 29  # Should handle February correctly


class TestCheckDigestSchedule:
    """Test digest scheduling logic"""
    
    def test_check_digest_schedule_due_users(self, db_session):
        """Test checking for users due for digest"""
        # Create users with past digest times
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        user1 = UserAccount(
            email="due1@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.DAILY,
            next_digest_at=past_time,
            is_active=True
        )
        user2 = UserAccount(
            email="due2@test.com",
            categories=["cs.LG"],
            frequency=DigestFrequency.WEEKLY,
            next_digest_at=past_time,
            is_active=True
        )
        # User not due yet
        future_time = datetime.utcnow() + timedelta(hours=1)
        user3 = UserAccount(
            email="notdue@test.com",
            categories=["cs.CV"],
            frequency=DigestFrequency.DAILY,
            next_digest_at=future_time,
            is_active=True
        )
        
        db_session.add_all([user1, user2, user3])
        db_session.commit()
        
        with patch('app.tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.send_digest_email_task') as mock_send_task:
                with patch('app.tasks.calculate_next_digest_time') as mock_calc_time:
                    future_digest_time = datetime.utcnow() + timedelta(days=1)
                    mock_calc_time.return_value = future_digest_time
                    
                    result = check_digest_schedule()
                    
                    assert result is True
                    # Should queue digest emails for 2 users (user1 and user2)
                    assert mock_send_task.delay.call_count == 2
                    
                    # Verify next_digest_at was updated
                    db_session.refresh(user1)
                    db_session.refresh(user2)
                    assert user1.next_digest_at == future_digest_time
                    assert user2.next_digest_at == future_digest_time
    
    def test_check_digest_schedule_inactive_users(self, db_session):
        """Test that inactive users are not processed"""
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        inactive_user = UserAccount(
            email="inactive@test.com",
            categories=["cs.AI"],
            frequency=DigestFrequency.DAILY,
            next_digest_at=past_time,
            is_active=False  # Inactive user
        )
        
        db_session.add(inactive_user)
        db_session.commit()
        
        with patch('app.tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.send_digest_email_task') as mock_send_task:
                result = check_digest_schedule()
                
                assert result is True
                # Should not queue any emails for inactive users
                mock_send_task.delay.assert_not_called()
    
    def test_check_digest_schedule_error_handling(self, db_session):
        """Test error handling in digest schedule check"""
        with patch('app.tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.UserAccount') as mock_user_account:
                # Simulate database error
                mock_user_account.query.side_effect = Exception("Database error")
                
                # Should handle error gracefully and rollback
                try:
                    check_digest_schedule()
                except Exception:
                    pytest.fail("check_digest_schedule should handle errors gracefully")


class TestSendDigestEmailTask:
    """Test send digest email task"""
    
    def test_send_digest_email_task_success(self, db_session):
        """Test successful digest email sending"""
        # Create user and papers
        user = UserAccount(
            email="digest@test.com",
            categories=["cs.AI", "cs.LG"],
            frequency=DigestFrequency.DAILY,
            is_active=True
        )
        
        papers = [
            Paper(
                arxiv_id="2024.0001v1",
                title="AI Paper 1",
                authors="Author 1",
                abstract="Abstract 1",
                category="cs.AI",
                published_at=datetime.utcnow()
            ),
            Paper(
                arxiv_id="2024.0002v1",
                title="LG Paper 1",
                authors="Author 2",
                abstract="Abstract 2",
                category="cs.LG",
                published_at=datetime.utcnow() - timedelta(hours=1)
            )
        ]
        
        db_session.add(user)
        db_session.add_all(papers)
        db_session.commit()
        
        with patch('app.tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.send_digest_email') as mock_send_email:
                result = send_digest_email_task(user.id)
                
                assert result is True
                mock_send_email.assert_called_once()
                
                # Verify the call arguments
                call_args = mock_send_email.call_args[0]
                called_user = call_args[0]
                called_papers = call_args[1]
                
                assert called_user.id == user.id
                assert len(called_papers) <= 5  # Should limit to 5 papers
    
    def test_send_digest_email_task_user_not_found(self, db_session):
        """Test digest email task when user not found"""
        with patch('app.tasks.SessionLocal', return_value=db_session):
            result = send_digest_email_task(999)  # Non-existent user ID
            
            assert result is False
    
    def test_send_digest_email_task_inactive_user(self, db_session):
        """Test digest email task for inactive user"""
        inactive_user = UserAccount(
            email="inactive@test.com",
            categories=["cs.AI"],
            is_active=False
        )
        
        db_session.add(inactive_user)
        db_session.commit()
        
        with patch('app.tasks.SessionLocal', return_value=db_session):
            result = send_digest_email_task(inactive_user.id)
            
            assert result is False
    
    def test_send_digest_email_task_no_papers(self, db_session):
        """Test digest email task when no papers match user categories"""
        user = UserAccount(
            email="nopapers@test.com",
            categories=["cs.AI"],  # No papers in this category
            is_active=True
        )
        
        # Add paper in different category
        paper = Paper(
            arxiv_id="2024.0003v1",
            title="CV Paper",
            authors="Author",
            abstract="Abstract",
            category="cs.CV",  # Different category
            published_at=datetime.utcnow()
        )
        
        db_session.add(user)
        db_session.add(paper)
        db_session.commit()
        
        with patch('app.tasks.SessionLocal', return_value=db_session):
            result = send_digest_email_task(user.id)
            
            assert result is False  # No matching papers
    
    def test_send_digest_email_task_paper_filtering(self, db_session):
        """Test that papers are filtered by user categories"""
        user = UserAccount(
            email="filtered@test.com",
            categories=["cs.AI"],  # Only interested in AI
            is_active=True
        )
        
        # Create papers in different categories
        ai_paper = Paper(
            arxiv_id="2024.ai.v1",
            title="AI Paper",
            authors="AI Author",
            abstract="AI Abstract",
            category="cs.AI",
            published_at=datetime.utcnow()
        )
        cv_paper = Paper(
            arxiv_id="2024.cv.v1",
            title="CV Paper",
            authors="CV Author",
            abstract="CV Abstract",
            category="cs.CV",  # Should be filtered out
            published_at=datetime.utcnow()
        )
        
        db_session.add_all([user, ai_paper, cv_paper])
        db_session.commit()
        
        with patch('app.tasks.SessionLocal', return_value=db_session):
            with patch('app.tasks.send_digest_email') as mock_send_email:
                result = send_digest_email_task(user.id)
                
                assert result is True
                
                # Verify only AI paper was included
                call_args = mock_send_email.call_args[0]
                called_papers = call_args[1]
                
                assert len(called_papers) == 1
                assert called_papers[0].category == "cs.AI"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])