from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, Header, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
import jwt
from datetime import datetime, timedelta

from .database import get_db, init_db
from .models import Paper, UserAccount, UserSaved, DigestFrequency
from .tasks import fetch_papers, process_summaries, calculate_next_digest_time
from .settings import settings

# Create FastAPI app
app = FastAPI(
    title="Research Digest API",
    description="API for the Research Digest platform",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class PaperResponse(BaseModel):
    id: int
    arxiv_id: str
    title: str
    authors: str
    abstract: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    published_at: datetime
    
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    categories: List[str]
    frequency: DigestFrequency = DigestFrequency.DAILY


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    categories: List[str]
    frequency: DigestFrequency
    next_digest_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    categories: Optional[List[str]] = None
    frequency: Optional[DigestFrequency] = None


# Helper functions
async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Get current user from session token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Extract email from authorization header - in a real app, you'd validate a JWT token
        # This is a simplified version for testing purposes
        email = authorization.split("Bearer ")[1]
        
        # Find user
        user = db.query(UserAccount).filter(UserAccount.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {"message": "Research Digest API is running"}


@app.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user or update existing user.
    
    - **email**: User's email address
    - **name**: User's name (optional)
    - **categories**: List of arXiv categories to follow
    - **frequency**: Digest frequency (DAILY, WEEKLY, MONTHLY)
    """
    # Check if user already exists
    existing_user = db.query(UserAccount).filter(UserAccount.email == user_data.email).first()
    
    if existing_user:
        # Update existing user
        existing_user.name = user_data.name or existing_user.name
        existing_user.categories = user_data.categories
        existing_user.frequency = user_data.frequency
        existing_user.is_active = True
        user = existing_user
    else:
        # Create new user
        user = UserAccount(
            email=user_data.email,
            name=user_data.name,
            categories=user_data.categories,
            frequency=user_data.frequency,
            is_active=True
        )
        db.add(user)
    
    # Calculate initial next_digest_at value
    user.next_digest_at = calculate_next_digest_time(user)
    
    db.commit()
    db.refresh(user)
    
    return user


@app.get("/profile", response_model=UserResponse)
async def get_profile(user: UserAccount = Depends(get_current_user)):
    """Get current user's profile."""
    return user


@app.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    
    - **name**: User's name (optional)
    - **categories**: List of arXiv categories to follow (optional)
    - **frequency**: Digest frequency (optional)
    """
    # Update fields if provided
    if user_data.name is not None:
        user.name = user_data.name
    
    if user_data.categories is not None:
        user.categories = user_data.categories
    
    frequency_changed = False
    if user_data.frequency is not None and user.frequency != user_data.frequency:
        user.frequency = user_data.frequency
        frequency_changed = True
    
    # Recalculate next_digest_at if frequency changed
    if frequency_changed:
        user.next_digest_at = calculate_next_digest_time(user)
    
    db.commit()
    db.refresh(user)
    
    return user


@app.get("/unsubscribe", response_model=dict)
async def unsubscribe(token: str, db: Session = Depends(get_db)):
    """Unsubscribe from digest emails using a token."""
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Check if token is for unsubscribe
        if payload.get("action") != "unsubscribe":
            raise HTTPException(status_code=400, detail="Invalid token")
        
        # Get user ID
        user_id = int(payload.get("sub"))
        
        # Find user
        user = db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user to inactive
        user.is_active = False
        db.commit()
        
        return {"message": "You have been unsubscribed successfully"}
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")


@app.get("/categories", response_model=List[str])
async def get_arxiv_categories():
    """Get list of available arXiv categories."""
    # Return a predefined list of arXiv categories
    return [
        # Physics
        "astro-ph", "cond-mat", "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th", "math-ph", "nlin", "nucl-ex", "nucl-th", "physics", "quant-ph",
        # Mathematics
        "math",
        # Computer Science
        "cs.AI", "cs.AR", "cs.CC", "cs.CE", "cs.CG", "cs.CL", "cs.CR", "cs.CV", "cs.CY", "cs.DB", 
        "cs.DC", "cs.DL", "cs.DM", "cs.DS", "cs.ET", "cs.FL", "cs.GL", "cs.GR", "cs.GT", "cs.HC", 
        "cs.IR", "cs.IT", "cs.LG", "cs.LO", "cs.MA", "cs.MM", "cs.MS", "cs.NA", "cs.NE", "cs.NI", 
        "cs.OH", "cs.OS", "cs.PF", "cs.PL", "cs.RO", "cs.SC", "cs.SD", "cs.SE", "cs.SI", "cs.SY",
        # Quantitative Biology
        "q-bio",
        # Quantitative Finance
        "q-fin",
        # Statistics
        "stat"
    ]


@app.post("/trigger/fetch")
async def trigger_fetch():
    """Manually trigger paper fetch task."""
    fetch_papers.delay()
    return {"message": "Paper fetch task triggered"}


@app.post("/trigger/summarize")
async def trigger_summarize(limit: int = 10):
    """Manually trigger summary processing task."""
    process_summaries.delay(limit)
    return {"message": f"Summary processing task triggered for {limit} papers"}


# For admin functionality
@app.get("/admin/users", response_model=List[UserResponse])
async def admin_get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: UserAccount = Depends(get_current_user)
):
    """Admin endpoint to get all users."""
    # Simple admin check - in production, use a proper role-based system
    if user.email not in settings.ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    users = db.query(UserAccount).offset(skip).limit(limit).all()
    return users


@app.get("/admin/stats", response_model=dict)
async def admin_get_stats(
    db: Session = Depends(get_db),
    user: UserAccount = Depends(get_current_user)
):
    """Admin endpoint to get system stats."""
    # Simple admin check
    if user.email not in settings.ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Get stats
    user_count = db.query(UserAccount).count()
    active_user_count = db.query(UserAccount).filter(UserAccount.is_active == True).count()
    paper_count = db.query(Paper).count()
    
    # Get frequency stats
    daily_count = db.query(UserAccount).filter(UserAccount.frequency == DigestFrequency.DAILY).count()
    weekly_count = db.query(UserAccount).filter(UserAccount.frequency == DigestFrequency.WEEKLY).count()
    monthly_count = db.query(UserAccount).filter(UserAccount.frequency == DigestFrequency.MONTHLY).count()
    
    # Get category distribution
    # This is a simplification - in a real system you'd use a more efficient query
    category_counts = {}
    users = db.query(UserAccount).all()
    for user in users:
        for category in user.categories:
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
    
    # Sort categories by popularity
    popular_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "user_count": user_count,
        "active_user_count": active_user_count,
        "paper_count": paper_count,
        "frequency_stats": {
            "daily": daily_count,
            "weekly": weekly_count,
            "monthly": monthly_count
        },
        "popular_categories": dict(popular_categories)
    } 