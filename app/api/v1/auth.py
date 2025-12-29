"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.auth import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    TokenResponse,
    UserResponse,
    MessageResponse,
    PasswordResetRequest,
    PasswordReset,
    PasswordChange,
)
from services.auth_service import AuthService
from api.deps import get_current_active_user
from models.user import User
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================
# REGISTRATION
# ============================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user and create their organization. Returns authentication tokens."
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user:
    
    - **email**: Valid email address (will be used for login)
    - **password**: Strong password (min 8 chars, must contain uppercase, lowercase, and digit)
    - **full_name**: User's full name
    - **organization_name**: Name of the organization
    - **industry**: Optional industry vertical
    
    Creates both user and organization. First user becomes organization owner.
    """
    auth_service = AuthService(db)
    
    try:
        # Register user
        user, organization = await auth_service.register_user(user_data)
        
        # Create tokens
        token_data = auth_service.create_tokens(user)
        
        # Prepare response
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=UserResponse.model_validate(user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# LOGIN
# ============================================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user with email and password. Returns authentication tokens."
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user:
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns access token (30 min) and refresh token (7 days).
    """
    auth_service = AuthService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    token_data = auth_service.create_tokens(user)
    
    return TokenResponse(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type=token_data["token_type"],
        expires_in=token_data["expires_in"],
        user=UserResponse.model_validate(user)
    )


# ============================================
# TOKEN REFRESH
# ============================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token:
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens.
    """
    auth_service = AuthService(db)
    
    # Refresh tokens
    new_token_data = await auth_service.refresh_access_token(
        token_data.refresh_token
    )
    
    if not new_token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user for response
    from core.security import decode_token
    import uuid
    
    payload = decode_token(new_token_data["access_token"])
    user_id = uuid.UUID(payload["sub"])
    user = await auth_service.get_user_by_id(user_id)
    
    return TokenResponse(
        access_token=new_token_data["access_token"],
        refresh_token=new_token_data["refresh_token"],
        token_type=new_token_data["token_type"],
        expires_in=new_token_data["expires_in"],
        user=UserResponse.model_validate(user)
    )


# ============================================
# LOGOUT
# ============================================

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Logout current user (client should delete tokens)"
)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user:
    
    - Client should delete stored tokens
    - For production, implement token blacklist using Redis
    
    Currently returns success message.
    """
    # In production, you would:
    # 1. Add token to blacklist in Redis
    # 2. Set expiration to match token expiration
    
    return MessageResponse(
        message="Successfully logged out"
    )


# ============================================
# GET CURRENT USER
# ============================================

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information:
    
    Requires valid access token in Authorization header.
    Returns user profile data.
    """
    return UserResponse.model_validate(current_user)


# ============================================
# PASSWORD RESET
# ============================================

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Request password reset email"
)
async def forgot_password(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset:
    
    - **email**: Registered email address
    
    Sends password reset email with token.
    Always returns success to prevent email enumeration.
    """
    auth_service = AuthService(db)
    
    # Request password reset
    reset_token = await auth_service.request_password_reset(request_data.email)
    
    if reset_token:
        # In production, send email with reset token
        # background_tasks.add_task(send_password_reset_email, request_data.email, reset_token)
        
        # For development, you might log the token
        if settings.ENVIRONMENT == "development":
            print(f"Password reset token for {request_data.email}: {reset_token}")
    
    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset password using reset token"
)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password:
    
    - **token**: Password reset token from email
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, and digit)
    
    Resets user password if token is valid.
    """
    auth_service = AuthService(db)
    
    # Reset password
    success = await auth_service.reset_password(
        reset_data.token,
        reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return MessageResponse(
        message="Password successfully reset"
    )


# ============================================
# CHANGE PASSWORD (AUTHENTICATED)
# ============================================

@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change password for authenticated user"
)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password (requires authentication):
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 chars, must contain uppercase, lowercase, and digit)
    
    Changes password for currently authenticated user.
    """
    auth_service = AuthService(db)
    
    # Change password
    success = await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return MessageResponse(
        message="Password successfully changed"
    )