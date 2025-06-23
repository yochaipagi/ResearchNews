import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Set up the database schema and pgvector extension."""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        try:
            # Attempt to create pgvector extension
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgvector;"))
                conn.commit()
                logger.info("pgvector extension created successfully")
        except Exception as e:
            logger.warning(f"Could not create pgvector extension: {e}")
            logger.warning("Proceeding without vector search capabilities")
        
        # Create tables
        from .models import Base
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error setting up database: {e}")
        return False


if __name__ == "__main__":
    setup_database() 