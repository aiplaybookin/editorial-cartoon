"""
API v1 routers
"""
from .auth import router as auth_router
from .campaigns import router as campaigns_router


__all__ = ["auth_router", "campaigns_router"]