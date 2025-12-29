"""
Authentication service layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Tuple
from datetime import datetime, timedelta
import uuid

from models.user import User
from models.organization import Organization
from schemas.auth import UserRegister, UserLogin
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    verify_password_reset_token,
    decode_token,
)
from core.config import settings


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_user(
        self,
        user_data: UserRegister
    ) -> Tuple[User, Organization]:
        """
        Register a new user and create their organization
        
        Args:
            user_data: User registration data
            
        Returns:
            Tuple of (User, Organization)
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Extract domain from email
        domain = user_data.email.split('@')[1] if '@' in user_data.email else None
        
        # Public email domains to ignore for organization domain
        PUBLIC_EMAIL_DOMAINS = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", 
            "icloud.com", "aol.com", "protonmail.com", "mail.com",
            "zoho.com", "yandex.com", "live.com"
        }
        
        if domain and domain.lower() in PUBLIC_EMAIL_DOMAINS:
            domain = None
        
        # Create organization
        organization = Organization(
            id=uuid.uuid4(),
            name=user_data.organization_name,
            domain=domain,
            industry=user_data.industry,
            subscription_tier="beta",
            is_active=True
        )
        self.db.add(organization)
        await self.db.flush()  # Flush to get organization.id
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            organization_id=organization.id,
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hash_password(user_data.password),
            role="owner",  # First user is owner
            is_active=True
        )
        self.db.add(user)
        
        await self.db.commit()
        await self.db.refresh(user)
        await self.db.refresh(organization)
        
        return user, organization
    
    async def authenticate_user(
        self,
        login_data: UserLogin
    ) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            login_data: Login credentials
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Get user by email
        stmt = select(User).where(User.email == login_data.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        # Check if user is active
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return user
    
    def create_tokens(self, user: User) -> dict:
        """
        Create access and refresh tokens for user
        
        Args:
            user: User object
            
        Returns:
            Dictionary with access_token, refresh_token, and expires_in
        """
        # Create token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "org_id": str(user.organization_id)
        }
        
        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def refresh_access_token(
        self,
        refresh_token: str
    ) -> Optional[dict]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token data or None if invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Get user
        stmt = select(User).where(User.id == uuid.UUID(user_id))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Create new tokens
        return self.create_tokens(user)
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User UUID
            
        Returns:
            User object or None
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User object or None
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def request_password_reset(self, email: str) -> Optional[str]:
        """
        Create password reset token for user
        
        Args:
            email: User email
            
        Returns:
            Password reset token or None if user not found
        """
        user = await self.get_user_by_email(email)
        
        if not user or not user.is_active:
            # Don't reveal if email exists
            return None
        
        # Create reset token
        reset_token = create_password_reset_token(email)
        
        return reset_token
    
    async def reset_password(
        self,
        token: str,
        new_password: str
    ) -> bool:
        """
        Reset user password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        # Verify token
        email = verify_password_reset_token(token)
        
        if not email:
            return False
        
        # Get user
        user = await self.get_user_by_email(email)
        
        if not user:
            return False
        
        # Update password
        user.password_hash = hash_password(new_password)
        await self.db.commit()
        
        return True
    
    async def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password (when logged in)
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        user = await self.get_user_by_id(user_id)
        
        if not user:
            return False
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return False
        
        # Update password
        user.password_hash = hash_password(new_password)
        await self.db.commit()
        
        return True