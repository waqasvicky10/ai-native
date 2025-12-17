# Pydantic schemas for API requests and responses
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# Enums
class UserLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Language(str, Enum):
    ENGLISH = "english"
    URDU = "urdu"

class ContentType(str, Enum):
    TEXT = "text"
    CODE = "code"
    DIAGRAM = "diagram"
    FORMULA = "formula"

# Base schemas
class BaseResponse(BaseModel):
    """Base response schema."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    """Error response schema."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# User schemas
class UserProfileCreate(BaseModel):
    """Schema for creating user profile."""
    background_level: UserLevel
    technical_background: str = Field(..., min_length=3, max_length=200)
    experience_years: int = Field(ge=0, le=50)
    learning_goals: List[str] = Field(..., min_items=1, max_items=10)
    interests: List[str] = Field(default=[], max_items=10)
    preferred_language: Language = Language.ENGLISH

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    background_level: Optional[UserLevel] = None
    technical_background: Optional[str] = Field(None, min_length=3, max_length=200)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    learning_goals: Optional[List[str]] = Field(None, max_items=10)
    interests: Optional[List[str]] = Field(None, max_items=10)
    preferred_language: Optional[Language] = None

class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    language: Optional[Language] = None
    content_personalization: Optional[bool] = None
    chatbot_enabled: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    theme: Optional[str] = Field(None, regex="^(light|dark)$")
    auto_translate: Optional[bool] = None

class UserResponse(BaseResponse):
    """User response schema."""
    user: Dict[str, Any]

# Authentication schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)
    profile: Optional[UserProfileCreate] = None

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class AuthResponse(BaseResponse):
    """Authentication response schema."""
    user: Dict[str, Any]
    token: str
    refresh_token: str

# RAG and Chatbot schemas
class ChatMessage(BaseModel):
    """Chat message schema."""
    role: str = Field(..., regex="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=5000)
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, max_length=1000)
    chapter_id: Optional[str] = None
    conversation_history: List[ChatMessage] = Field(default=[], max_items=20)
    user_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseResponse):
    """Chat response schema."""
    message: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[Dict[str, Any]] = Field(default=[])
    suggested_followups: List[str] = Field(default=[])
    processing_time: float

# Translation schemas
class TranslationRequest(BaseModel):
    """Translation request schema."""
    text: str = Field(..., min_length=1, max_length=10000)
    target_language: Language = Language.URDU
    preserve_technical_terms: bool = True
    context: Optional[str] = Field(None, max_length=500)

class TranslationResponse(BaseResponse):
    """Translation response schema."""
    translated_text: str
    source_language: str
    target_language: str
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    preserved_terms: List[str] = Field(default=[])

# Personalization schemas
class PersonalizationRequest(BaseModel):
    """Personalization request schema."""
    content: str = Field(..., min_length=1, max_length=20000)
    user_level: UserLevel
    user_background: str
    learning_goals: List[str]
    context: Optional[str] = Field(None, max_length=500)

class PersonalizationResponse(BaseResponse):
    """Personalization response schema."""
    personalized_content: str
    adaptation_reasons: List[str] = Field(default=[])
    difficulty_adjustment: Optional[str] = None

# Content schemas
class ContentMetadata(BaseModel):
    """Content metadata schema."""
    chapter_id: str
    section: str
    content_type: ContentType
    difficulty: UserLevel
    tags: List[str] = Field(default=[])
    estimated_reading_time: Optional[int] = Field(None, ge=1)

class ContentDocument(BaseModel):
    """Content document schema."""
    content: str = Field(..., min_length=1)
    metadata: ContentMetadata

class ContentIndexRequest(BaseModel):
    """Content indexing request schema."""
    documents: List[ContentDocument] = Field(..., min_items=1, max_items=100)

class ContentIndexResponse(BaseResponse):
    """Content indexing response schema."""
    indexed_count: int
    document_ids: List[str]
    processing_time: float

class ContentSearchRequest(BaseModel):
    """Content search request schema."""
    query: str = Field(..., min_length=1, max_length=500)
    chapter_id: Optional[str] = None
    content_type: Optional[ContentType] = None
    difficulty: Optional[UserLevel] = None
    limit: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class ContentSearchResponse(BaseResponse):
    """Content search response schema."""
    results: List[Dict[str, Any]]
    query: str
    total_results: int
    processing_time: float

# Progress tracking schemas
class ProgressUpdate(BaseModel):
    """Progress update schema."""
    chapter_id: str
    time_spent: int = Field(ge=0)
    completed: Optional[bool] = None
    assessment_score: Optional[float] = Field(None, ge=0.0, le=100.0)

class BookmarkCreate(BaseModel):
    """Bookmark creation schema."""
    chapter_id: str
    section: str
    note: Optional[str] = Field(None, max_length=500)

class BookmarkResponse(BaseResponse):
    """Bookmark response schema."""
    bookmark: Dict[str, Any]

class ProgressResponse(BaseResponse):
    """Progress response schema."""
    progress: Dict[str, Any]

# Health check schemas
class ServiceHealth(BaseModel):
    """Service health schema."""
    service: str
    status: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

class HealthCheckResponse(BaseResponse):
    """Health check response schema."""
    status: str
    services: Dict[str, Union[str, Dict[str, Any]]]
    version: str