"""
Authentication schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


# ============================================
# REQUEST SCHEMAS
# ============================================

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    organization_name: str = Field(..., min_length=2, max_length=255, description="Organization name")
    industry: Optional[str] = Field(None, max_length=100, description="Industry vertical")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "vikash@techcorp.com",
                "password": "SecurePass123!",
                "full_name": "Vikash Kumar",
                "organization_name": "TechCorp Inc",
                "industry": "pharmaceutical"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "vikash@techcorp.com",
                "password": "SecurePass123!"
            }
        }


class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
            }
        }


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "vikash@techcorp.com"
            }
        }


class PasswordReset(BaseModel):
    """Schema for resetting password"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset-token-here",
                "new_password": "NewSecurePass123!"
            }
        }


class PasswordChange(BaseModel):
    """Schema for changing password (when logged in)"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


# ============================================
# RESPONSE SCHEMAS
# ============================================

from uuid import UUID

# ...

class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: UUID
    email: str
    full_name: Optional[str]
    role: str
    organization_id: UUID
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "vikash@techcorp.com",
                "full_name": "Vikash Kumar",
                "role": "owner",
                "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                "is_active": True,
                "created_at": "2024-12-28T10:00:00Z",
                "last_login": "2024-12-29T09:30:00Z"
            }
        }


class OrganizationResponse(BaseModel):
    """Schema for organization data in responses"""
    id: UUID
    name: str
    domain: Optional[str]
    industry: Optional[str]
    subscription_tier: str
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "vikash@techcorp.com",
                    "full_name": "Vikash Kumar",
                    "role": "owner",
                    "organization_id": "660e8400-e29b-41d4-a716-446655440000",
                    "is_active": True,
                    "created_at": "2024-12-28T10:00:00Z",
                    "last_login": None
                }
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation successful"
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials",
                "error_code": "INVALID_CREDENTIALS"
            }
        }