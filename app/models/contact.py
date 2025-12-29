"""
Contact and recipient models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List
from datetime import datetime
import uuid

from .base import Base, TimestampMixin, UUIDMixin


class SubscriptionStatus(str):
    """Subscription status constants"""
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"


class SendStatus(str):
    """Email send status constants"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


class ContactList(Base, UUIDMixin, TimestampMixin):
    """
    Contact list for organizing contacts
    """
    __tablename__ = "contact_lists"

    # Foreign Key
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to organization"
    )
    
    # List Details
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="List name"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="List description"
    )
    total_contacts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of contacts in list"
    )
    
    # Creator
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the list"
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="contact_lists"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="contact_lists_created"
    )
    list_members: Mapped[List["ContactListMember"]] = relationship(
        "ContactListMember",
        back_populates="contact_list",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<ContactList(id={self.id}, name='{self.name}', contacts={self.total_contacts})>"


class Contact(Base, UUIDMixin, TimestampMixin):
    """
    Contact model representing email recipients
    """
    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint('organization_id', 'email', name='uq_org_contact_email'),
    )

    # Foreign Key
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to organization"
    )
    
    # Contact Information
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Contact email address"
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="First name"
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Last name"
    )
    company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Company name"
    )
    job_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Job title"
    )
    
    # Segmentation
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        comment="Tags for segmentation"
    )
    custom_fields: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Custom fields for flexible data"
    )
    
    # Subscription Status
    subscription_status: Mapped[str] = mapped_column(
        String(50),
        default=SubscriptionStatus.SUBSCRIBED,
        nullable=False,
        index=True,
        comment="Subscription status"
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether email is verified"
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="contacts"
    )
    list_memberships: Mapped[List["ContactListMember"]] = relationship(
        "ContactListMember",
        back_populates="contact",
        cascade="all, delete-orphan"
    )
    campaign_recipients: Mapped[List["CampaignRecipient"]] = relationship(
        "CampaignRecipient",
        back_populates="contact",
        cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.email
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, email='{self.email}', status='{self.subscription_status}')>"


class ContactListMember(Base, UUIDMixin):
    """
    Junction table for many-to-many relationship between contacts and lists
    """
    __tablename__ = "contact_list_members"
    __table_args__ = (
        UniqueConstraint('contact_id', 'list_id', name='uq_contact_list'),
    )

    # Foreign Keys
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to contact"
    )
    list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contact_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to contact list"
    )
    
    # Metadata
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        comment="When contact was added to list"
    )
    
    # Relationships
    contact: Mapped["Contact"] = relationship(
        "Contact",
        back_populates="list_memberships"
    )
    contact_list: Mapped["ContactList"] = relationship(
        "ContactList",
        back_populates="list_members"
    )
    
    def __repr__(self) -> str:
        return f"<ContactListMember(contact_id={self.contact_id}, list_id={self.list_id})>"


class CampaignRecipient(Base, UUIDMixin):
    """
    Track individual recipients for each campaign with engagement metrics
    """
    __tablename__ = "campaign_recipients"
    __table_args__ = (
        UniqueConstraint('campaign_id', 'contact_id', name='uq_campaign_contact'),
    )

    # Foreign Keys
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to campaign"
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to contact"
    )
    
    # Sending Status
    send_status: Mapped[str] = mapped_column(
        String(50),
        default=SendStatus.PENDING,
        nullable=False,
        index=True,
        comment="Send status: pending, sent, failed, bounced"
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When email was sent"
    )
    
    # Open Tracking
    opened: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether email was opened"
    )
    open_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times opened"
    )
    first_opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="First open timestamp"
    )
    last_opened_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last open timestamp"
    )
    
    # Click Tracking
    clicked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether any link was clicked"
    )
    click_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of clicks"
    )
    first_clicked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="First click timestamp"
    )
    last_clicked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last click timestamp"
    )
    
    # Unsubscribe Tracking
    unsubscribed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether recipient unsubscribed"
    )
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Unsubscribe timestamp"
    )
    
    # Personalization
    personalized_content: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Personalized content for this recipient"
    )
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="recipients"
    )
    contact: Mapped["Contact"] = relationship(
        "Contact",
        back_populates="campaign_recipients"
    )
    events: Mapped[List["EmailEvent"]] = relationship(
        "EmailEvent",
        back_populates="recipient",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<CampaignRecipient(campaign_id={self.campaign_id}, contact_id={self.contact_id}, status='{self.send_status}')>"