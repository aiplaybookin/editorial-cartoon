"""
Campaign models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List
from datetime import datetime
import uuid
import enum

from models.base import Base, TimestampMixin, UUIDMixin


class CampaignStatus(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    ARCHIVED = "archived"


class CampaignGoal(str, enum.Enum):
    """Campaign goal enumeration"""
    LEAD_GENERATION = "lead_generation"
    PRODUCT_LAUNCH = "product_launch"
    NURTURE = "nurture"
    REENGAGEMENT = "reengagement"
    EVENT_PROMOTION = "event_promotion"


class Campaign(Base, UUIDMixin, TimestampMixin):
    """
    Campaign model representing an email marketing campaign
    """
    __tablename__ = "campaigns"

    # Foreign Keys
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to organization"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the campaign"
    )
    
    # Campaign Identity
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Campaign name"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Campaign description"
    )
    status: Mapped[CampaignStatus] = mapped_column(
        SQLEnum(CampaignStatus, native_enum=False, length=50),
        default=CampaignStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Campaign status"
    )
    
    # Campaign Objectives
    primary_goal: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Primary campaign goal"
    )
    target_audience_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description of target audience"
    )
    success_criteria: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Success criteria for the campaign"
    )
    
    # Metrics
    target_metrics: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Target metrics: open_rate, click_rate, conversion_rate"
    )
    estimated_recipients: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Estimated number of recipients"
    )
    
    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="When campaign is scheduled to send"
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When campaign was actually sent"
    )
    
    # AI Generation Context
    ai_context: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="AI generation context and parameters"
    )
    generation_iterations: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of AI generation iterations"
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="campaigns"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="campaigns_created",
        foreign_keys=[created_by]
    )
    objectives: Mapped[List["CampaignObjective"]] = relationship(
        "CampaignObjective",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    templates: Mapped[List["EmailTemplate"]] = relationship(
        "EmailTemplate",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    recipients: Mapped[List["CampaignRecipient"]] = relationship(
        "CampaignRecipient",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    analytics: Mapped[Optional["CampaignAnalytics"]] = relationship(
        "CampaignAnalytics",
        back_populates="campaign",
        uselist=False,
        cascade="all, delete-orphan"
    )
    ai_generation_jobs: Mapped[List["AIGenerationJob"]] = relationship(
        "AIGenerationJob",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    @property
    def is_editable(self) -> bool:
        """Check if campaign can be edited"""
        return self.status in [CampaignStatus.DRAFT, CampaignStatus.REVIEW, CampaignStatus.PAUSED]
    
    @property
    def is_sendable(self) -> bool:
        """Check if campaign is ready to be sent"""
        return self.status in [CampaignStatus.SCHEDULED, CampaignStatus.PAUSED]


class CampaignObjective(Base, UUIDMixin, TimestampMixin):
    """
    Campaign objectives and KPIs
    """
    __tablename__ = "campaign_objectives"

    # Foreign Key
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to campaign"
    )
    
    # Objective Details
    objective_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Type: primary, secondary"
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Objective description"
    )
    kpi_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="KPI name: open_rate, click_rate, conversion, revenue"
    )
    target_value: Mapped[float] = mapped_column(
        nullable=False,
        comment="Target value for the KPI"
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Priority level (1 = highest)"
    )
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="objectives"
    )
    
    def __repr__(self) -> str:
        return f"<CampaignObjective(id={self.id}, kpi='{self.kpi_name}', target={self.target_value})>"