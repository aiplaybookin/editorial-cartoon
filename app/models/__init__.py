"""
SQLAlchemy ORM Models
"""
from models.base import Base, TimestampMixin, UUIDMixin

# Import all models to ensure they're registered with Base
from models.organization import Organization, CompanyProfile
from models.user import User
from models.campaign import Campaign, CampaignObjective
from models.template import EmailTemplate, EmailRevision, AIGenerationJob
from models.contact import Contact, ContactList, ContactListMember, CampaignRecipient
from models.analytics import CampaignAnalytics, EmailEvent, AuditLog

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