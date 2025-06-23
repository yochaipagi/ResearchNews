from pydantic_settings import BaseSettings
from typing import Optional, Literal, List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql://researchfeed:researchfeed@localhost:5432/researchfeed"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM Provider (gemini or openai)
    LLM_PROVIDER: Literal["gemini", "openai"] = "gemini"
    
    # Google Gemini
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Email settings
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: str = "digest@researchdigest.com"
    EMAIL_FROM_NAME: str = "Research Digest"
    
    # Web host - used for unsubscribe links
    BASE_URL: str = "http://localhost:3000"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"  # Change in production!
    
    # Admin settings
    ADMIN_EMAILS: List[str] = ["yochai.pagi1997@gmail.com"]  # Add your email here
    
    # arXiv API settings
    ARXIV_API_URL: str = "https://export.arxiv.org/api/query"
    ARXIV_USER_AGENT: str = "research-digest/0.1 (contact@yourapp.com)"
    ARXIV_CATEGORIES: list[str] = ["cs.CL", "cs.AI", "cs.LG"]
    
    # Fetch interval in seconds (3 hours)
    FETCH_INTERVAL: int = 10800
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings() 