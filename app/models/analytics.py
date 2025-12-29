"""
Analytics and tracking models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, Numeric, Index, DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from typing import Optional, List
from datetime import datetime
import uuid

from .base import Base, TimestampMixin, UUIDMixin


class CampaignAnalytics(Base, UUIDMixin, TimestampMixin):
    """
    Aggregated analytics for campaigns
    """
    __tablename__ = "campaign_analytics"

    # Foreign Key (One-to-One with Campaign)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Reference to campaign"
    )
    
    # Send Metrics
    total_sent: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total emails sent"
    )
    total_delivered: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total emails delivered"
    )
    total_bounced: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total bounced emails"
    )
    total_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total failed sends"
    )
    
    # Engagement Metrics
    total_opens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total opens (including duplicates)"
    )
    unique_opens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Unique opens"
    )
    total_clicks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total clicks (including duplicates)"
    )
    unique_clicks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Unique clicks"
    )
    total_unsubscribes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total unsubscribes"
    )
    total_spam_reports: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total spam complaints"
    )
    
    # Calculated Rates (stored as percentages)
    delivery_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Delivery rate percentage"
    )
    open_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Open rate percentage"
    )
    click_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Click rate percentage"
    )
    click_to_open_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Click-to-open rate percentage"
    )
    unsubscribe_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Unsubscribe rate percentage"
    )
    
    # Goal Achievement
    goal_achieved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether campaign goal was achieved"
    )
    goal_completion_rate: Mapped[Optional[float]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,
        comment="Goal completion percentage"
    )
    
    # Metadata
    last_calculated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time analytics were calculated"
    )
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="analytics"
    )
    
    def calculate_rates(self) -> None:
        """Calculate all rate metrics"""
        # Delivery rate
        if self.total_sent > 0:
            self.delivery_rate = (self.total_delivered / self.total_sent) * 100
        
        # Open rate (based on delivered)
        if self.total_delivered > 0:
            self.open_rate = (self.unique_opens / self.total_delivered) * 100
        
        # Click rate (based on delivered)
        if self.total_delivered > 0:
            self.click_rate = (self.unique_clicks / self.total_delivered) * 100
        
        # Click-to-open rate
        if self.unique_opens > 0:
            self.click_to_open_rate = (self.unique_clicks / self.unique_opens) * 100
        
        # Unsubscribe rate
        if self.total_delivered > 0:
            self.unsubscribe_rate = (self.total_unsubscribes / self.total_delivered) * 100
        
        self.last_calculated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<CampaignAnalytics(campaign_id={self.campaign_id}, sent={self.total_sent}, opens={self.unique_opens})>"


class EmailEvent(Base, UUIDMixin):
    """
    Individual email events for detailed tracking
    """
    __tablename__ = "email_events"
    __table_args__ = (
        Index('idx_email_events_recipient', 'campaign_recipient_id'),
        Index('idx_email_events_type', 'event_type'),
        Index('idx_email_events_occurred', 'occurred_at'),
    )

    # Foreign Key
    campaign_recipient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaign_recipients.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to campaign recipient"
    )
    
    # Event Details
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Event type: sent, delivered, opened, clicked, bounced, unsubscribed, complained"
    )
    
    # Event Data (flexible JSON for event-specific data)
    event_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Event-specific data: link_url, bounce_type, user_agent, etc."
    )
    
    # Timestamps
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="When event occurred"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="When event was recorded"
    )
    
    # Relationships
    recipient: Mapped["CampaignRecipient"] = relationship(
        "CampaignRecipient",
        back_populates="events"
    )
    
    def __repr__(self) -> str:
        return f"<EmailEvent(id={self.id}, type='{self.event_type}', occurred_at={self.occurred_at})>"


class AuditLog(Base, UUIDMixin):
    """
    Audit log for tracking all actions in the system
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_org', 'organization_id'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_created', 'created_at'),
    )

    # Foreign Keys
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to organization"
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who performed the action"
    )
    
    # Action Details
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Action performed: campaign_created, email_sent, etc."
    )
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Entity type: campaign, template, contact"
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID of the entity affected"
    )
    
    # Change Details
    changes: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Before/after snapshot of changes"
    )
    
    # Request Details
    ip_address: Mapped[Optional[str]] = mapped_column(
        INET,
        nullable=True,
        comment="IP address of request"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User agent string"
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="When action was performed"
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="audit_logs"
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', entity_type='{self.entity_type}')>"