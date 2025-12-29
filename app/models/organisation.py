"""
Organization and Company Profile models
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List
import uuid

from models.base import Base, TimestampMixin, UUIDMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    """
    Organization/Account model for multi-tenancy
    Each organization represents a company using the platform
    """
    __tablename__ = "organizations"

    # Basic Information
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Organization name")
    domain: Mapped[Optional[str]] = mapped_column(
        String(255), 
        unique=True, 
        nullable=True,
        comment="Organization email domain"
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True,
        comment="Industry vertical"
    )
    company_size: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        comment="Company size category: startup, small, medium, enterprise"
    )
    website_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True,
        comment="Company website"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Whether organization is active"
    )
    subscription_tier: Mapped[str] = mapped_column(
        String(50), 
        default="beta", 
        nullable=False,
        comment="Subscription tier: beta, starter, pro, enterprise"
    )
    
    # AI Settings (flexible JSON for model preferences, tone settings, etc.)
    ai_settings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="AI model preferences and settings"
    )
    
    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User", 
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    company_profile: Mapped[Optional["CompanyProfile"]] = relationship(
        "CompanyProfile",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan"
    )
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    contacts: Mapped[List["Contact"]] = relationship(
        "Contact",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    contact_lists: Mapped[List["ContactList"]] = relationship(
        "ContactList",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="organization",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', tier='{self.subscription_tier}')>"


class CompanyProfile(Base, UUIDMixin, TimestampMixin):
    """
    Company profile containing brand voice, target audience, and other context
    Used by AI to generate personalized content
    """
    __tablename__ = "company_profiles"

    # Foreign Key
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Reference to organization"
    )
    
    # Brand Information
    brand_voice: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description of brand voice and tone"
    )
    value_propositions: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        comment="Key value propositions"
    )
    pain_points: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        comment="Customer pain points the company solves"
    )
    competitive_advantages: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        comment="Competitive advantages"
    )
    
    # Target Audience (JSON for flexibility)
    target_audience: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Target audience details: personas, industries, company sizes"
    )
    
    # Products/Services (JSON array of objects)
    product_services: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Products and services offered"
    )
    
    # Brand Guidelines (JSON for colors, fonts, writing style, etc.)
    brand_guidelines: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Brand guidelines including colors, fonts, writing style"
    )
    
    # Compliance
    compliance_requirements: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        comment="Compliance requirements: GDPR, CAN-SPAM, industry-specific"
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="company_profile"
    )
    
    def __repr__(self) -> str:
        return f"<CompanyProfile(id={self.id}, org_id={self.organization_id})>"