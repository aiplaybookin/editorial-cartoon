"""
User model for authentication and authorization
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List
from datetime import datetime
import uuid

from .base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model for platform access
    Users belong to organizations and have roles
    """
    __tablename__ = "users"

    # Organization relationship
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to organization"
    )
    
    # User Information
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address (login)"
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User full name"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Hashed password"
    )
    
    # Role and Status
    role: Mapped[str] = mapped_column(
        String(50),
        default="member",
        nullable=False,
        comment="User role: owner, admin, member, viewer"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether user account is active"
    )
    
    # Activity tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last login timestamp"
    )
    
    # User Preferences (JSON for flexibility)
    preferences: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="User preferences: UI settings, notifications, etc."
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="users"
    )
    campaigns_created: Mapped[List["Campaign"]] = relationship(
        "Campaign",
        back_populates="creator",
        foreign_keys="Campaign.created_by"
    )
    templates_created: Mapped[List["EmailTemplate"]] = relationship(
        "EmailTemplate",
        back_populates="creator",
        foreign_keys="EmailTemplate.created_by"
    )
    templates_reviewed: Mapped[List["EmailTemplate"]] = relationship(
        "EmailTemplate",
        back_populates="reviewer",
        foreign_keys="EmailTemplate.reviewed_by"
    )
    ai_generation_jobs: Mapped[List["AIGenerationJob"]] = relationship(
        "AIGenerationJob",
        back_populates="creator"
    )
    contact_lists_created: Mapped[List["ContactList"]] = relationship(
        "ContactList",
        back_populates="creator"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission based on role"""
        role_permissions = {
            "owner": ["all"],
            "admin": ["create", "read", "update", "delete", "approve"],
            "member": ["create", "read", "update"],
            "viewer": ["read"]
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return "all" in user_permissions or permission in user_permissions