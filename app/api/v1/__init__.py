"""
API v1 routers
"""
from .auth import router as auth_router

__all__ = ["auth_router"]