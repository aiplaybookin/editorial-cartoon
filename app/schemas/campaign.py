"""
Campaign schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID

# ============================================
# ENUMS
# ============================================

class CampaignStatusEnum(str, Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    ARCHIVED = "archived"


class CampaignGoalEnum(str, Enum):
    """Campaign goal enumeration"""
    LEAD_GENERATION = "lead_generation"
    PRODUCT_LAUNCH = "product_launch"
    NURTURE = "nurture"
    REENGAGEMENT = "reengagement"
    EVENT_PROMOTION = "event_promotion"


class ObjectiveTypeEnum(str, Enum):
    """Objective type enumeration"""
    PRIMARY = "primary"
    SECONDARY = "secondary"


class KPINameEnum(str, Enum):
    """KPI name enumeration"""
    OPEN_RATE = "open_rate"
    CLICK_RATE = "click_rate"
    CONVERSION = "conversion"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"


# ============================================
# OBJECTIVE SCHEMAS
# ============================================

class CampaignObjectiveBase(BaseModel):
    """Base schema for campaign objectives"""
    objective_type: ObjectiveTypeEnum = Field(..., description="Objective type: primary or secondary")
    description: str = Field(..., min_length=1, description="Objective description")
    kpi_name: KPINameEnum = Field(..., description="KPI to measure")
    target_value: float = Field(..., ge=0, description="Target value for KPI")
    priority: int = Field(default=1, ge=1, le=10, description="Priority level (1=highest)")


class CampaignObjectiveCreate(CampaignObjectiveBase):
    """Schema for creating campaign objective"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "objective_type": "primary",
                "description": "Generate qualified demo requests",
                "kpi_name": "conversion",
                "target_value": 5.0,
                "priority": 1
            }
        }


class CampaignObjectiveUpdate(BaseModel):
    """Schema for updating campaign objective"""
    objective_type: Optional[ObjectiveTypeEnum] = None
    description: Optional[str] = Field(None, min_length=1)
    kpi_name: Optional[KPINameEnum] = None
    target_value: Optional[float] = Field(None, ge=0)
    priority: Optional[int] = Field(None, ge=1, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_value": 7.0,
                "priority": 1
            }
        }

class CampaignObjectiveResponse(CampaignObjectiveBase):
    """Schema for campaign objective response"""
    id: UUID
    campaign_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "campaign_id": "660e8400-e29b-41d4-a716-446655440001",
                "objective_type": "primary",
                "description": "Generate qualified demo requests",
                "kpi_name": "conversion",
                "target_value": 5.0,
                "priority": 1,
                "created_at": "2024-12-28T10:00:00Z"
            }
        }


# ============================================
# CAMPAIGN SCHEMAS
# ============================================

class CampaignBase(BaseModel):
    """Base schema for campaigns"""
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: Optional[str] = Field(None, description="Campaign description")
    primary_goal: CampaignGoalEnum = Field(..., description="Primary campaign goal")
    target_audience_description: str = Field(..., min_length=1, description="Target audience description")
    success_criteria: Optional[str] = Field(None, description="Success criteria")


class CampaignCreate(CampaignBase):
    """Schema for creating campaign"""
    objectives: List[CampaignObjectiveCreate] = Field(default_factory=list, description="Campaign objectives")
    target_metrics: Optional[dict] = Field(None, description="Target metrics")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule send time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Q1 Product Launch - AI Documentation Suite",
                "description": "Introducing our new AI-powered clinical documentation platform",
                "primary_goal": "product_launch",
                "target_audience_description": "Clinical research managers at mid-to-large pharmaceutical companies",
                "success_criteria": "20+ demo requests with at least 5 from enterprise pharma",
                "objectives": [
                    {
                        "objective_type": "primary",
                        "description": "Generate qualified demo requests",
                        "kpi_name": "conversion",
                        "target_value": 5.0,
                        "priority": 1
                    },
                    {
                        "objective_type": "secondary",
                        "description": "Achieve strong engagement",
                        "kpi_name": "open_rate",
                        "target_value": 30.0,
                        "priority": 2
                    }
                ],
                "target_metrics": {
                    "open_rate": 30.0,
                    "click_rate": 10.0,
                    "conversion_rate": 3.0
                },
                "scheduled_at": "2025-01-15T09:00:00Z"
            }
        }


class CampaignUpdate(BaseModel):
    """Schema for updating campaign"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    primary_goal: Optional[CampaignGoalEnum] = None
    target_audience_description: Optional[str] = Field(None, min_length=1)
    success_criteria: Optional[str] = None
    target_metrics: Optional[dict] = None
    scheduled_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Q1 Product Launch - Updated",
                "target_metrics": {
                    "open_rate": 35.0,
                    "click_rate": 12.0
                }
            }
        }


class CampaignResponse(CampaignBase):
    """Schema for campaign response"""
    id: UUID
    organization_id: UUID
    status: CampaignStatusEnum
    estimated_recipients: Optional[int]
    target_metrics: Optional[dict]
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    ai_context: Optional[dict]
    generation_iterations: int
    objectives: List[CampaignObjectiveResponse] = []
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "organization_id": "770e8400-e29b-41d4-a716-446655440002",
                "name": "Q1 Product Launch",
                "description": "Product launch campaign",
                "status": "draft",
                "primary_goal": "product_launch",
                "target_audience_description": "Clinical research managers",
                "success_criteria": "20+ demo requests",
                "estimated_recipients": 1500,
                "target_metrics": {
                    "open_rate": 30.0,
                    "click_rate": 10.0
                },
                "scheduled_at": None,
                "sent_at": None,
                "ai_context": None,
                "generation_iterations": 0,
                "objectives": [],
                "created_by": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2024-12-28T10:00:00Z",
                "updated_at": "2024-12-28T10:00:00Z"
            }
        }


class CampaignListResponse(BaseModel):
    """Schema for paginated campaign list"""
    campaigns: List[CampaignResponse]
    total: int = Field(..., description="Total number of campaigns")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaigns": [],
                "total": 45,
                "page": 1,
                "per_page": 20,
                "pages": 3
            }
        }


class CampaignScheduleRequest(BaseModel):
    """Schema for scheduling campaign"""
    scheduled_at: datetime = Field(..., description="When to send the campaign")
    
    @validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future"""
        if v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "scheduled_at": "2025-01-15T09:00:00Z"
            }
        }


class CampaignStatsResponse(BaseModel):
    """Schema for campaign statistics"""
    total_campaigns: int
    draft: int
    scheduled: int
    sent: int
    active: int
    archived: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_campaigns": 45,
                "draft": 12,
                "scheduled": 5,
                "sent": 25,
                "active": 3,
                "archived": 0
            }
        }