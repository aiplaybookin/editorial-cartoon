"""
Email template and AI generation models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Optional, List
from datetime import datetime
import uuid
import enum

from .base import Base, TimestampMixin, UUIDMixin


class TemplateStatus(str, enum.Enum):
    """Template status enumeration"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class GeneratedBy(str, enum.Enum):
    """Content generation source"""
    AI = "ai"
    HUMAN = "human"
    HYBRID = "hybrid"


class EmailTemplate(Base, UUIDMixin, TimestampMixin):
    """
    Email template with versioning support
    Each campaign can have multiple template versions
    """
    __tablename__ = "email_templates"
    __table_args__ = (
        UniqueConstraint('campaign_id', 'version', name='uq_campaign_version'),
    )

    # Foreign Key
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to campaign"
    )
    
    # Version Control
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Version number for tracking iterations"
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this is the current active version"
    )
    
    # Email Metadata
    subject_line: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Email subject line"
    )
    preview_text: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Email preview text (preheader)"
    )
    from_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Sender name"
    )
    from_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Sender email address"
    )
    reply_to_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Reply-to email address"
    )
    
    # Email Content
    html_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="HTML email content"
    )
    plain_text_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Plain text email content"
    )
    
    # AI Generation Metadata
    generated_by: Mapped[str] = mapped_column(
        String(50),
        default=GeneratedBy.AI.value,
        nullable=False,
        comment="Content generation source: ai, human, hybrid"
    )
    ai_model_used: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="AI model used for generation"
    )
    generation_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Prompt used for AI generation"
    )
    ai_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="AI generation metadata: temperature, tokens, confidence"
    )
    
    # Review and Approval
    status: Mapped[TemplateStatus] = mapped_column(
        String(50),
        default=TemplateStatus.DRAFT.value,
        nullable=False,
        index=True,
        comment="Template status"
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who reviewed the template"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When template was reviewed"
    )
    review_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Review notes and feedback"
    )
    
    # Creator
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the template"
    )
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="templates"
    )
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="templates_created",
        foreign_keys=[created_by]
    )
    reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="templates_reviewed",
        foreign_keys=[reviewed_by]
    )
    revisions: Mapped[List["EmailRevision"]] = relationship(
        "EmailRevision",
        back_populates="template",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<EmailTemplate(id={self.id}, campaign_id={self.campaign_id}, version={self.version}, current={self.is_current})>"


class EmailRevision(Base, UUIDMixin, TimestampMixin):
    """
    Track revisions and changes to email templates
    """
    __tablename__ = "email_revisions"

    # Foreign Key
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to email template"
    )
    
    # Revision Details
    revision_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: ai_regeneration, manual_edit, ab_variant"
    )
    previous_content: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Snapshot of previous version"
    )
    changes_made: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description of changes made"
    )
    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for revision"
    )
    
    # Creator
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created the revision"
    )
    
    # Relationships
    template: Mapped["EmailTemplate"] = relationship(
        "EmailTemplate",
        back_populates="revisions"
    )
    
    def __repr__(self) -> str:
        return f"<EmailRevision(id={self.id}, template_id={self.template_id}, type='{self.revision_type}')>"


class AIGenerationJob(Base, UUIDMixin, TimestampMixin):
    """
    Track AI generation jobs for async processing
    """
    __tablename__ = "ai_generation_jobs"

    # Foreign Keys
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to campaign"
    )
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("email_templates.id", ondelete="SET NULL"),
        nullable=True,
        comment="Reference to generated template (if completed)"
    )
    
    # Job Details
    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type: initial_generation, revision, ab_variant, subject_line_test"
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
        comment="Status: pending, processing, completed, failed"
    )
    
    # Input
    user_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User's generation prompt"
    )
    context: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Generation context: company profile, campaign objectives"
    )
    
    # Output
    generated_content: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Generated content variants"
    )
    ai_model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="AI model used"
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Confidence score of generation"
    )
    
    # Metadata
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When job started processing"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When job completed"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if job failed"
    )
    tokens_used: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of tokens used"
    )
    
    # Creator
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who initiated the job"
    )
    
    # Relationships
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="ai_generation_jobs"
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="ai_generation_jobs"
    )
    
    def __repr__(self) -> str:
        return f"<AIGenerationJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"