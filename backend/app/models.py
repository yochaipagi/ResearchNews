from datetime import datetime, time
from typing import List, Optional
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Time, ForeignKey, BigInteger, ARRAY, Text, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class DigestFrequency(str, Enum):
    """Enum for digest frequency options."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class Paper(Base):
    """Paper model for storing arXiv papers."""
    
    __tablename__ = "paper"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    arxiv_id = Column(String, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    authors = Column(Text)
    abstract = Column(Text)  # Full abstract 
    summary = Column(Text)   # LLM-generated TL;DR (≤ 60 words)
    embedding = Column(Vector(768), nullable=True)
    category = Column(String)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_by = relationship("UserSaved", back_populates="paper")
    
    def __repr__(self):
        return f"<Paper(id={self.id}, arxiv_id={self.arxiv_id}, title={self.title[:30]}...)>"


class UserAccount(Base):
    """User account model."""
    
    __tablename__ = "user_account"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)  # Added name field
    categories = Column(ARRAY(String), nullable=False)  # Make nullable=False as per spec
    frequency = Column(SQLEnum(DigestFrequency), default=DigestFrequency.DAILY)  # Added digest frequency
    next_digest_at = Column(DateTime)  # Added next digest timestamp
    is_active = Column(Boolean, default=True)  # For unsubscribe functionality
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    saved_papers = relationship("UserSaved", back_populates="user")
    
    def __repr__(self):
        return f"<UserAccount(id={self.id}, email={self.email})>"


class UserSaved(Base):
    """Model for papers saved by users."""
    
    __tablename__ = "user_saved"
    
    user_id = Column(BigInteger, ForeignKey("user_account.id"), primary_key=True)
    paper_id = Column(BigInteger, ForeignKey("paper.id"), primary_key=True)
    saved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserAccount", back_populates="saved_papers")
    paper = relationship("Paper", back_populates="saved_by")
    
    def __repr__(self):
        return f"<UserSaved(user_id={self.user_id}, paper_id={self.paper_id})>" 