#!/usr/bin/env python
from app.database import engine, SessionLocal
from app.models import Base, UserAccount, DigestFrequency
from app.settings import settings
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Create all tables if they don't exist."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")
    
    # Check if admin user exists, create if not
    db = SessionLocal()
    try:
        # Use single admin email
        admin_email = settings.ADMIN_EMAIL
        admin = db.query(UserAccount).filter(UserAccount.email == admin_email).first()
        if not admin:
            logger.info(f"Creating admin user: {admin_email}")
            admin = UserAccount(
                email=admin_email,
                name="Admin",
                categories=["cs.AI", "cs.CL", "cs.LG"],  # Default categories
                frequency=DigestFrequency.DAILY,
                next_digest_at=datetime.utcnow() + timedelta(days=1),
                is_active=True
            )
            db.add(admin)
            db.commit()
            logger.info(f"Admin user created: {admin_email}")
        else:
            logger.info(f"Admin user already exists: {admin_email}")
    except Exception as e:
        logger.error(f"Error setting up admin user: {e}")
        db.rollback()
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    setup_database()
    print("Database setup complete.") 