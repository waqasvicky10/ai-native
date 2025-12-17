# User database models using SQLAlchemy
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth users
    name = Column(String, nullable=True)
    image = Column(String, nullable=True)
    
    # OAuth fields
    provider = Column(String, nullable=True)  # 'google', 'github', 'credentials'
    provider_id = Column(String, nullable=True)
    
    # Profile data (stored as JSON)
    profile_data = Column(JSON, nullable=True)
    preferences_data = Column(JSON, nullable=True)
    progress_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "image": self.image,
            "provider": self.provider,
            "profile": self.profile_data or {},
            "preferences": self.preferences_data or {},
            "progress": self.progress_data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
        }

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    session_token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, default=func.now())
    
    # Session metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class UserProfile(Base):
    """User profile and background information."""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # Foreign key to users table
    background_level = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    technical_background = Column(Text, nullable=False)
    experience_years = Column(Integer, nullable=False)
    learning_goals = Column(JSON, nullable=False)  # List of learning goals
    interests = Column(JSON, nullable=True)  # List of interests
    preferred_language = Column(String(50), default="english")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPreferences(Base):
    """User preferences and settings."""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # Foreign key to users table
    language = Column(String(50), default="english")
    content_personalization = Column(Boolean, default=True)
    chatbot_enabled = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    theme = Column(String(20), default="light")
    auto_translate = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserProgress(Base):
    """User progress tracking for chapters."""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # Foreign key to users table
    chapter_id = Column(String(100), nullable=False)
    time_spent = Column(Integer, default=0)  # Time in minutes
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    assessment_score = Column(String, nullable=True)  # Score out of 100 (using String for compatibility)
    assessment_completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserBookmark(Base):
    """User bookmarks for chapter sections."""
    __tablename__ = "user_bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # Foreign key to users table
    chapter_id = Column(String(100), nullable=False)
    section = Column(String(255), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)