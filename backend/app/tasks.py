import logging
import asyncio
from datetime import datetime, timedelta, time
from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import Session
import calendar
from dateutil.relativedelta import relativedelta

from .settings import settings
from .database import SessionLocal
from .models import UserAccount, Paper, DigestFrequency
from .ingestion import ingest_papers_for_categories
from .summarise import process_unsummarized_papers
from .email import send_digest_email

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery('research_feed')
celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL

# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
    'fetch-papers-every-3-hours': {
        'task': 'app.tasks.fetch_papers',
        'schedule': crontab(minute=0, hour='*/3'),  # Every 3 hours as per spec
    },
    'process-summaries-every-hour': {
        'task': 'app.tasks.process_summaries',
        'schedule': crontab(minute=30, hour='*'),  # Every hour at 30 minutes past
    },
    'check-digest-schedule-every-15-minutes': {
        'task': 'app.tasks.check_digest_schedule',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes as per spec section 9
    },
}


@celery_app.task(name='app.tasks.fetch_papers')
def fetch_papers():
    """Task to fetch papers from arXiv."""
    logger.info("Starting paper fetch task")
    
    # Run the async function in the event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ingest_papers_for_categories())
    
    logger.info("Paper fetch task completed")
    return True


@celery_app.task(name='app.tasks.process_summaries')
def process_summaries(limit: int = 10):
    """Task to process unsummarized papers."""
    logger.info(f"Starting summary processing task (limit: {limit})")
    
    # Run the async function in the event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_unsummarized_papers(limit))
    
    logger.info("Summary processing task completed")
    return True


def calculate_next_digest_time(user: UserAccount) -> datetime:
    """
    Calculate the next digest time based on frequency.
    
    As per spec section 9:
    - DAILY → tomorrow at user.digest_time
    - WEEKLY → +7 days at digest_time
    - MONTHLY → +1 month at digest_time (same D-of-M or last day)
    """
    now = datetime.utcnow()
    
    # Get user's preferred time of day (or use current time if not set)
    # We're using the current time components as the user's digest_time preference
    digest_hour = now.hour
    digest_minute = now.minute
    digest_second = now.second
    
    if user.frequency == DigestFrequency.DAILY:
        # Tomorrow at same time
        tomorrow = now.date() + timedelta(days=1)
        next_time = datetime.combine(tomorrow, time(hour=digest_hour, minute=digest_minute, second=digest_second))
    
    elif user.frequency == DigestFrequency.WEEKLY:
        # Next week same day and time
        next_week = now.date() + timedelta(days=7)
        next_time = datetime.combine(next_week, time(hour=digest_hour, minute=digest_minute, second=digest_second))
    
    elif user.frequency == DigestFrequency.MONTHLY:
        # Next month, same day (or last day of month if current day doesn't exist)
        next_month = now.month + 1
        next_year = now.year
        
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        # Get the last day of next month
        _, last_day = calendar.monthrange(next_year, next_month)
        
        # Use the current day or the last day of the month, whichever is smaller
        next_day = min(now.day, last_day)
        
        next_time = datetime(next_year, next_month, next_day, 
                             digest_hour, digest_minute, digest_second)
    
    else:
        # Default to tomorrow
        tomorrow = now.date() + timedelta(days=1)
        next_time = datetime.combine(tomorrow, time(hour=digest_hour, minute=digest_minute, second=digest_second))
    
    return next_time


@celery_app.task(name='app.tasks.check_digest_schedule')
def check_digest_schedule():
    """Check and send digests for users whose next_digest_at time has passed."""
    logger.info("Starting digest schedule check")
    
    now = datetime.utcnow()
    db = SessionLocal()
    
    try:
        # Find users with next_digest_at <= now
        users_due = db.query(UserAccount).filter(
            UserAccount.next_digest_at <= now,
            UserAccount.is_active == True
        ).all()
        
        logger.info(f"Found {len(users_due)} users due for digest")
        
        for user in users_due:
            # Queue up an individual email sending task
            send_digest_email_task.delay(user.id)
            
            # Update the next digest time
            user.next_digest_at = calculate_next_digest_time(user)
        
        # Commit the updates
        db.commit()
        
    except Exception as e:
        logger.error(f"Error during digest schedule check: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()
    
    logger.info("Digest schedule check completed")
    return True


@celery_app.task(name='app.tasks.send_digest_email_task')
def send_digest_email_task(user_id: int):
    """
    Task to send a digest email for a user.
    
    As per spec section 7:
    1. Get papers that match user's categories
    2. Order by published_at DESC
    3. Choose top 5 for the email
    """
    logger.info(f"Starting digest email task for user {user_id}")
    
    db = SessionLocal()
    
    try:
        # Get the user
        user = db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if not user or not user.is_active:
            logger.warning(f"User {user_id} not found or not active")
            return False
        
        # As per the pseudocode in section 7 of the spec:
        # SELECT * FROM paper WHERE category && user.categories ORDER BY published_at DESC LIMIT 5
        papers = db.query(Paper).filter(
            Paper.category.in_(user.categories)
        ).order_by(
            Paper.published_at.desc()
        ).limit(5).all()
        
        if not papers:
            logger.warning(f"No papers found for user {user_id}")
            return False
        
        # Send the email
        send_digest_email(user, papers)
        
        logger.info(f"Digest email sent for user {user_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending digest email for user {user_id}: {e}")
        raise
    
    finally:
        db.close() 