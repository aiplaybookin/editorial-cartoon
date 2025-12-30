"""
Pydantic schemas
"""
from .auth import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    PasswordResetRequest,
    PasswordReset,
    PasswordChange,
    UserResponse,
    OrganizationResponse,
    TokenResponse,
    MessageResponse,
    ErrorResponse,
)

from .campaign import (
    CampaignStatusEnum,
    CampaignGoalEnum,
    ObjectiveTypeEnum,
    KPINameEnum,
    CampaignObjectiveCreate,
    CampaignObjectiveUpdate,
    CampaignObjectiveResponse,
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    CampaignScheduleRequest,
    CampaignStatsResponse,
)
__all__ = [
    # Auth
    "UserRegister",
    "UserLogin",
    "TokenRefresh",
    "PasswordResetRequest",
    "PasswordReset",
    "PasswordChange",
    "UserResponse",
    "OrganizationResponse",
    "TokenResponse",
    "MessageResponse",
    "ErrorResponse",
    # Campaign
    "CampaignStatusEnum",
    "CampaignGoalEnum",
    "ObjectiveTypeEnum",
    "KPINameEnum",
    "CampaignObjectiveCreate",
    "CampaignObjectiveUpdate",
    "CampaignObjectiveResponse",
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignListResponse",
    "CampaignScheduleRequest",
    "CampaignStatsResponse",
]