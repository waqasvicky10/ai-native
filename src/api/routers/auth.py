# Authentication API router
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import bcrypt
import jwt
import os

from ..database import get_db
from ..models.user import User, UserProfile, UserPreferences
from ..schemas import (
    LoginRequest, RegisterRequest, AuthResponse, 
    UserProfileCreate, UserProfileUpdate, UserPreferencesUpdate,
    UserResponse, BaseResponse
)

router = APIRouter()
security = HTTPBearer()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "development_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
REFRESH_TOKEN_EXPIRATION_DAYS = 30

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: int, email: str) -> str:
    """Create JWT refresh token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Creates user account with optional profile information.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(request.password)
        
        # Create user
        user = User(
            email=request.email,
            name=request.name,
            password_hash=hashed_password,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.flush()  # Get user ID
        
        # Create user profile if provided
        if request.profile:
            profile = UserProfile(
                user_id=user.id,
                background_level=request.profile.background_level.value,
                technical_background=request.profile.technical_background,
                experience_years=request.profile.experience_years,
                learning_goals=request.profile.learning_goals,
                interests=request.profile.interests,
                preferred_language=request.profile.preferred_language.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(profile)
        
        # Create default user preferences
        preferences = UserPreferences(
            user_id=user.id,
            language=request.profile.preferred_language.value if request.profile else "english",
            content_personalization=True,
            chatbot_enabled=True,
            notifications_enabled=True,
            theme="light",
            auto_translate=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(preferences)
        
        db.commit()
        
        # Generate tokens
        access_token = create_access_token(user.id, user.email)
        refresh_token = create_refresh_token(user.id, user.email)
        
        # Prepare user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "profile": {
                "background_level": profile.background_level if request.profile else None,
                "technical_background": profile.technical_background if request.profile else None,
                "experience_years": profile.experience_years if request.profile else None,
                "learning_goals": profile.learning_goals if request.profile else [],
                "interests": profile.interests if request.profile else [],
                "preferred_language": profile.preferred_language if request.profile else "english"
            } if request.profile else None,
            "preferences": {
                "language": preferences.language,
                "content_personalization": preferences.content_personalization,
                "chatbot_enabled": preferences.chatbot_enabled,
                "notifications_enabled": preferences.notifications_enabled,
                "theme": preferences.theme,
                "auto_translate": preferences.auto_translate
            }
        }
        
        return AuthResponse(
            user=user_data,
            token=access_token,
            refresh_token=refresh_token,
            message="User registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return tokens.
    """
    try:
        # Find user
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        # Get user profile and preferences
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user.id).first()
        
        db.commit()
        
        # Generate tokens
        access_token = create_access_token(user.id, user.email)
        refresh_token = create_refresh_token(user.id, user.email)
        
        # Prepare user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "created_at": user.created_at.isoformat(),
            "profile": {
                "background_level": profile.background_level,
                "technical_background": profile.technical_background,
                "experience_years": profile.experience_years,
                "learning_goals": profile.learning_goals,
                "interests": profile.interests,
                "preferred_language": profile.preferred_language
            } if profile else None,
            "preferences": {
                "language": preferences.language,
                "content_personalization": preferences.content_personalization,
                "chatbot_enabled": preferences.chatbot_enabled,
                "notifications_enabled": preferences.notifications_enabled,
                "theme": preferences.theme,
                "auto_translate": preferences.auto_translate
            } if preferences else None
        }
        
        return AuthResponse(
            user=user_data,
            token=access_token,
            refresh_token=refresh_token,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    try:
        payload = verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Verify user still exists and is active
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        new_access_token = create_access_token(user.id, user.email)
        
        return {
            "success": True,
            "token": new_access_token,
            "message": "Token refreshed successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    """
    try:
        # Get user profile and preferences
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
        
        user_data = {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "is_active": current_user.is_active,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "created_at": current_user.created_at.isoformat(),
            "profile": {
                "background_level": profile.background_level,
                "technical_background": profile.technical_background,
                "experience_years": profile.experience_years,
                "learning_goals": profile.learning_goals,
                "interests": profile.interests,
                "preferred_language": profile.preferred_language
            } if profile else None,
            "preferences": {
                "language": preferences.language,
                "content_personalization": preferences.content_personalization,
                "chatbot_enabled": preferences.chatbot_enabled,
                "notifications_enabled": preferences.notifications_enabled,
                "theme": preferences.theme,
                "auto_translate": preferences.auto_translate
            } if preferences else None
        }
        
        return UserResponse(user=user_data)
        
    except Exception as e:
        print(f"Error getting user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    request: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information.
    """
    try:
        # Get or create profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        
        if not profile:
            # Create new profile
            profile = UserProfile(
                user_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.add(profile)
        
        # Update profile fields
        if request.background_level is not None:
            profile.background_level = request.background_level.value
        if request.technical_background is not None:
            profile.technical_background = request.technical_background
        if request.experience_years is not None:
            profile.experience_years = request.experience_years
        if request.learning_goals is not None:
            profile.learning_goals = request.learning_goals
        if request.interests is not None:
            profile.interests = request.interests
        if request.preferred_language is not None:
            profile.preferred_language = request.preferred_language.value
        
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Return updated user info
        return await get_current_user_info(current_user, db)
        
    except Exception as e:
        db.rollback()
        print(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.put("/preferences", response_model=UserResponse)
async def update_user_preferences(
    request: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user preferences.
    """
    try:
        # Get or create preferences
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
        
        if not preferences:
            # Create new preferences
            preferences = UserPreferences(
                user_id=current_user.id,
                created_at=datetime.utcnow()
            )
            db.add(preferences)
        
        # Update preference fields
        if request.language is not None:
            preferences.language = request.language.value
        if request.content_personalization is not None:
            preferences.content_personalization = request.content_personalization
        if request.chatbot_enabled is not None:
            preferences.chatbot_enabled = request.chatbot_enabled
        if request.notifications_enabled is not None:
            preferences.notifications_enabled = request.notifications_enabled
        if request.theme is not None:
            preferences.theme = request.theme
        if request.auto_translate is not None:
            preferences.auto_translate = request.auto_translate
        
        preferences.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Return updated user info
        return await get_current_user_info(current_user, db)
        
    except Exception as e:
        db.rollback()
        print(f"Error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Preferences update failed"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (client should discard tokens).
    """
    return BaseResponse(message="Logout successful")

@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account and all associated data.
    """
    try:
        # Delete user profile
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).delete()
        
        # Delete user preferences
        db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).delete()
        
        # Delete user
        db.delete(current_user)
        
        db.commit()
        
        return BaseResponse(message="Account deleted successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )