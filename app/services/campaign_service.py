"""
Campaign service layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime
import uuid
import math

from models.campaign import Campaign, CampaignObjective, CampaignStatus
from models.user import User
from schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignObjectiveCreate,
    CampaignObjectiveUpdate,
    CampaignStatusEnum,
)


class CampaignService:
    """Service for campaign operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_campaign(
        self,
        organization_id: uuid.UUID,
        created_by: uuid.UUID,
        campaign_data: CampaignCreate
    ) -> Campaign:
        """
        Create a new campaign with objectives
        
        Args:
            organization_id: Organization UUID
            created_by: User UUID who is creating the campaign
            campaign_data: Campaign creation data
            
        Returns:
            Created campaign
        """
        # Create campaign
        campaign = Campaign(
            id=uuid.uuid4(),
            organization_id=organization_id,
            created_by=created_by,
            name=campaign_data.name,
            description=campaign_data.description,
            primary_goal=campaign_data.primary_goal.value,
            target_audience_description=campaign_data.target_audience_description,
            success_criteria=campaign_data.success_criteria,
            target_metrics=campaign_data.target_metrics,
            scheduled_at=campaign_data.scheduled_at,
            status=CampaignStatus.DRAFT
        )
        self.db.add(campaign)
        await self.db.flush()
        
        # Create objectives
        for obj_data in campaign_data.objectives:
            objective = CampaignObjective(
                id=uuid.uuid4(),
                campaign_id=campaign.id,
                objective_type=obj_data.objective_type.value,
                description=obj_data.description,
                kpi_name=obj_data.kpi_name.value,
                target_value=obj_data.target_value,
                priority=obj_data.priority
            )
            self.db.add(objective)
        
        await self.db.commit()
        await self.db.refresh(campaign)
        
        # Load objectives
        stmt = select(Campaign).where(Campaign.id == campaign.id).options(
            selectinload(Campaign.objectives)
        )
        result = await self.db.execute(stmt)
        campaign = result.scalar_one()
        
        return campaign
    
    async def get_campaign(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> Optional[Campaign]:
        """
        Get a campaign by ID
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID (for access control)
            
        Returns:
            Campaign or None if not found
        """
        stmt = (
            select(Campaign)
            .where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.organization_id == organization_id
                )
            )
            .options(selectinload(Campaign.objectives))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_campaigns(
        self,
        organization_id: uuid.UUID,
        status: Optional[List[CampaignStatusEnum]] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None
    ) -> Tuple[List[Campaign], int]:
        """
        List campaigns with filtering and pagination
        
        Args:
            organization_id: Organization UUID
            status: Optional list of statuses to filter by
            page: Page number (1-indexed)
            per_page: Items per page
            sort_by: Field to sort by
            order: Sort order (asc/desc)
            search: Search term for name/description
            
        Returns:
            Tuple of (campaigns list, total count)
        """
        # Build query
        query = select(Campaign).where(Campaign.organization_id == organization_id)
        
        # Apply status filter
        if status:
            status_values = [s.value for s in status]
            query = query.where(Campaign.status.in_(status_values))
        
        # Apply search
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Campaign.name.ilike(search_pattern),
                    Campaign.description.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        sort_column = getattr(Campaign, sort_by, Campaign.created_at)
        if order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Load objectives
        query = query.options(selectinload(Campaign.objectives))
        
        # Execute query
        result = await self.db.execute(query)
        campaigns = result.scalars().all()
        
        return list(campaigns), total
    
    async def update_campaign(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        campaign_data: CampaignUpdate
    ) -> Optional[Campaign]:
        """
        Update a campaign
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID (for access control)
            campaign_data: Update data
            
        Returns:
            Updated campaign or None if not found
        """
        campaign = await self.get_campaign(campaign_id, organization_id)
        
        if not campaign:
            return None
        
        # Check if campaign is editable
        if not campaign.is_editable:
            raise ValueError(f"Cannot edit campaign in {campaign.status.value} status")
        
        # Update fields
        update_data = campaign_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(campaign, field):
                if field == "primary_goal" and value:
                    setattr(campaign, field, value.value)
                else:
                    setattr(campaign, field, value)
        
        campaign.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(campaign)
        
        return campaign
    
    async def delete_campaign(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> bool:
        """
        Delete a campaign
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID (for access control)
            
        Returns:
            True if deleted, False if not found
        """
        campaign = await self.get_campaign(campaign_id, organization_id)
        
        if not campaign:
            return False
        
        # Check if campaign can be deleted
        if campaign.status in [CampaignStatus.SENDING, CampaignStatus.SENT]:
            raise ValueError(f"Cannot delete campaign in {campaign.status.value} status")
        
        await self.db.delete(campaign)
        await self.db.commit()
        
        return True
    
    async def duplicate_campaign(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        created_by: uuid.UUID
    ) -> Campaign:
        """
        Duplicate a campaign
        
        Args:
            campaign_id: Campaign UUID to duplicate
            organization_id: Organization UUID
            created_by: User UUID creating the duplicate
            
        Returns:
            New duplicated campaign
        """
        original = await self.get_campaign(campaign_id, organization_id)
        
        if not original:
            raise ValueError("Campaign not found")
        
        # Create duplicate
        duplicate = Campaign(
            id=uuid.uuid4(),
            organization_id=organization_id,
            created_by=created_by,
            name=f"{original.name} (Copy)",
            description=original.description,
            primary_goal=original.primary_goal,
            target_audience_description=original.target_audience_description,
            success_criteria=original.success_criteria,
            target_metrics=original.target_metrics,
            status=CampaignStatus.DRAFT
        )
        self.db.add(duplicate)
        await self.db.flush()
        
        # Duplicate objectives
        for obj in original.objectives:
            new_obj = CampaignObjective(
                id=uuid.uuid4(),
                campaign_id=duplicate.id,
                objective_type=obj.objective_type,
                description=obj.description,
                kpi_name=obj.kpi_name,
                target_value=obj.target_value,
                priority=obj.priority
            )
            self.db.add(new_obj)
        
        await self.db.commit()
        await self.db.refresh(duplicate)
        
        # Load objectives
        stmt = select(Campaign).where(Campaign.id == duplicate.id).options(
            selectinload(Campaign.objectives)
        )
        result = await self.db.execute(stmt)
        duplicate = result.scalar_one()
        
        return duplicate
    
    async def change_campaign_status(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        new_status: CampaignStatusEnum
    ) -> Optional[Campaign]:
        """
        Change campaign status
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            new_status: New status to set
            
        Returns:
            Updated campaign or None if not found
        """
        campaign = await self.get_campaign(campaign_id, organization_id)
        
        if not campaign:
            return None
        
        # Validate status transition
        self._validate_status_transition(campaign.status, new_status)
        
        campaign.status = new_status
        campaign.updated_at = datetime.utcnow()
        
        # Set sent_at if sending
        if new_status == CampaignStatusEnum.SENT:
            campaign.sent_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(campaign)
        
        return campaign
    
    def _validate_status_transition(
        self,
        current_status: CampaignStatus,
        new_status: CampaignStatusEnum
    ):
        """Validate if status transition is allowed"""
        # Define allowed transitions
        allowed_transitions = {
            CampaignStatus.DRAFT: [
                CampaignStatusEnum.GENERATING,
                CampaignStatusEnum.REVIEW,
                CampaignStatusEnum.SCHEDULED,
                CampaignStatusEnum.ARCHIVED
            ],
            CampaignStatus.GENERATING: [
                CampaignStatusEnum.DRAFT,
                CampaignStatusEnum.REVIEW
            ],
            CampaignStatus.REVIEW: [
                CampaignStatusEnum.DRAFT,
                CampaignStatusEnum.SCHEDULED,
                CampaignStatusEnum.ARCHIVED
            ],
            CampaignStatus.SCHEDULED: [
                CampaignStatusEnum.SENDING,
                CampaignStatusEnum.PAUSED,
                CampaignStatusEnum.ARCHIVED
            ],
            CampaignStatus.SENDING: [
                CampaignStatusEnum.SENT,
                CampaignStatusEnum.PAUSED
            ],
            CampaignStatus.SENT: [
                CampaignStatusEnum.ARCHIVED
            ],
            CampaignStatus.PAUSED: [
                CampaignStatusEnum.SCHEDULED,
                CampaignStatusEnum.SENDING,
                CampaignStatusEnum.ARCHIVED
            ],
            CampaignStatus.ARCHIVED: []
        }
        
        if new_status not in allowed_transitions.get(current_status, []):
            raise ValueError(
                f"Cannot transition from {current_status.value} to {new_status.value}"
            )
    
    async def schedule_campaign(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        scheduled_at: datetime
    ) -> Optional[Campaign]:
        """
        Schedule a campaign for sending
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            scheduled_at: When to send the campaign
            
        Returns:
            Updated campaign or None if not found
        """
        campaign = await self.get_campaign(campaign_id, organization_id)
        
        if not campaign:
            return None
        
        # Validate scheduled time
        if scheduled_at <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")
        
        campaign.scheduled_at = scheduled_at
        campaign.status = CampaignStatus.SCHEDULED
        campaign.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(campaign)
        
        return campaign
    
    async def get_campaign_stats(
        self,
        organization_id: uuid.UUID
    ) -> dict:
        """
        Get campaign statistics for organization
        
        Args:
            organization_id: Organization UUID
            
        Returns:
            Dictionary with campaign statistics
        """
        # Get total count
        total_query = select(func.count()).select_from(Campaign).where(
            Campaign.organization_id == organization_id
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()
        
        # Get counts by status
        status_query = (
            select(
                Campaign.status,
                func.count(Campaign.id)
            )
            .where(Campaign.organization_id == organization_id)
            .group_by(Campaign.status)
        )
        status_result = await self.db.execute(status_query)
        status_counts = {status: count for status, count in status_result}
        
        return {
            "total_campaigns": total,
            "draft": status_counts.get(CampaignStatus.DRAFT, 0),
            "scheduled": status_counts.get(CampaignStatus.SCHEDULED, 0),
            "sent": status_counts.get(CampaignStatus.SENT, 0),
            "active": (
                status_counts.get(CampaignStatus.SENDING, 0) +
                status_counts.get(CampaignStatus.SCHEDULED, 0)
            ),
            "archived": status_counts.get(CampaignStatus.ARCHIVED, 0)
        }
    
    # ============================================
    # CAMPAIGN OBJECTIVES
    # ============================================
    
    async def create_objective(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        objective_data: CampaignObjectiveCreate
    ) -> CampaignObjective:
        """
        Create a campaign objective
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            objective_data: Objective data
            
        Returns:
            Created objective
        """
        # Verify campaign exists and belongs to organization
        campaign = await self.get_campaign(campaign_id, organization_id)
        if not campaign:
            raise ValueError("Campaign not found")
        
        objective = CampaignObjective(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            objective_type=objective_data.objective_type.value,
            description=objective_data.description,
            kpi_name=objective_data.kpi_name.value,
            target_value=objective_data.target_value,
            priority=objective_data.priority
        )
        self.db.add(objective)
        await self.db.commit()
        await self.db.refresh(objective)
        
        return objective
    
    async def update_objective(
        self,
        objective_id: uuid.UUID,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        objective_data: CampaignObjectiveUpdate
    ) -> Optional[CampaignObjective]:
        """
        Update a campaign objective
        
        Args:
            objective_id: Objective UUID
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            objective_data: Update data
            
        Returns:
            Updated objective or None if not found
        """
        # Verify campaign exists
        campaign = await self.get_campaign(campaign_id, organization_id)
        if not campaign:
            return None
        
        # Get objective
        stmt = select(CampaignObjective).where(
            and_(
                CampaignObjective.id == objective_id,
                CampaignObjective.campaign_id == campaign_id
            )
        )
        result = await self.db.execute(stmt)
        objective = result.scalar_one_or_none()
        
        if not objective:
            return None
        
        # Update fields
        update_data = objective_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(objective, field):
                if field in ["objective_type", "kpi_name"] and value:
                    setattr(objective, field, value.value)
                else:
                    setattr(objective, field, value)
        
        await self.db.commit()
        await self.db.refresh(objective)
        
        return objective
    
    async def delete_objective(
        self,
        objective_id: uuid.UUID,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> bool:
        """
        Delete a campaign objective
        
        Args:
            objective_id: Objective UUID
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            
        Returns:
            True if deleted, False if not found
        """
        # Verify campaign exists
        campaign = await self.get_campaign(campaign_id, organization_id)
        if not campaign:
            return False
        
        # Get objective
        stmt = select(CampaignObjective).where(
            and_(
                CampaignObjective.id == objective_id,
                CampaignObjective.campaign_id == campaign_id
            )
        )
        result = await self.db.execute(stmt)
        objective = result.scalar_one_or_none()
        
        if not objective:
            return False
        
        await self.db.delete(objective)
        await self.db.commit()
        
        return True