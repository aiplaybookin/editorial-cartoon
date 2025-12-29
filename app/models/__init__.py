"""
SQLAlchemy ORM Models
"""
from app.models.base import Base, TimestampMixin, UUIDMixin

# Import all models to ensure they're registered with Base
from app.models.organization import Organization, CompanyProfile
from app.models.user import User
from app.models.campaign import Campaign, CampaignObjective
from app.models.template import EmailTemplate, EmailRevision, AIGenerationJob
from app.models.contact import Contact, ContactList, ContactListMember, CampaignRecipient
from app.models.analytics import CampaignAnalytics, EmailEvent, AuditLog

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # Organization
    "Organization",
    "CompanyProfile",
    # User
    "User",
    # Campaign
    "Campaign",
    "CampaignObjective",
    # Template
    "EmailTemplate",
    "EmailRevision",
    "AIGenerationJob",
    # Contact
    "Contact",
    "ContactList",
    "ContactListMember",
    "CampaignRecipient",
    # Analytics
    "CampaignAnalytics",
    "EmailEvent",
    "AuditLog",
]