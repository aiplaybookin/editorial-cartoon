"""
Campaign endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from core.database import get_db
from schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignListResponse,
    CampaignScheduleRequest,
    CampaignStatsResponse,
    CampaignStatusEnum,
    CampaignObjectiveCreate,
    CampaignObjectiveUpdate,
    CampaignObjectiveResponse,
)
from schemas.auth import MessageResponse
from services.campaign_service import CampaignService
from api.deps import get_current_active_user, require_member
from models.user import User
import math

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


# ============================================
# CAMPAIGN CRUD
# ============================================

@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create campaign",
    description="Create a new email campaign with objectives"
)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new campaign:
    
    - **name**: Campaign name (required)
    - **description**: Campaign description
    - **primary_goal**: Campaign objective (lead_generation, product_launch, etc.)
    - **target_audience_description**: Description of target audience (required)
    - **success_criteria**: Success criteria for the campaign
    - **objectives**: List of campaign objectives with KPIs
    - **target_metrics**: Target metrics (open_rate, click_rate, etc.)
    - **scheduled_at**: Optional schedule send time
    
    Requires authentication and member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign = await campaign_service.create_campaign(
            organization_id=current_user.organization_id,
            created_by=current_user.id,
            campaign_data=campaign_data
        )
        return CampaignResponse.model_validate(campaign)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=CampaignListResponse,
    summary="List campaigns",
    description="List all campaigns with filtering, searching, and pagination"
)
async def list_campaigns(
    status_filter: Optional[List[CampaignStatusEnum]] = Query(None, alias="status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|name|scheduled_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List campaigns with filtering and pagination:
    
    **Query Parameters:**
    - **status**: Filter by campaign status (can specify multiple, e.g., ?status=draft&status=scheduled)
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)
    - **sort_by**: Sort field (created_at, updated_at, name, scheduled_at)
    - **order**: Sort order (asc, desc)
    - **search**: Search term for campaign name or description
    
    Returns paginated list of campaigns with total count and page info.
    """
    campaign_service = CampaignService(db)
    
    campaigns, total = await campaign_service.list_campaigns(
        organization_id=current_user.organization_id,
        status=status_filter,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        search=search
    )
    
    # Calculate pagination info
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    return CampaignListResponse(
        campaigns=[CampaignResponse.model_validate(c) for c in campaigns],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get(
    "/stats",
    response_model=CampaignStatsResponse,
    summary="Get campaign statistics",
    description="Get campaign statistics for the organization"
)
async def get_campaign_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get campaign statistics:
    
    Returns counts of campaigns by status and overall statistics.
    Useful for dashboard widgets and overview pages.
    """
    campaign_service = CampaignService(db)
    
    stats = await campaign_service.get_campaign_stats(
        organization_id=current_user.organization_id
    )
    
    return CampaignStatsResponse(**stats)


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Get campaign",
    description="Get a specific campaign by ID"
)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a campaign by ID:
    
    - **campaign_id**: UUID of the campaign
    
    Returns full campaign details including objectives.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    campaign = await campaign_service.get_campaign(
        campaign_id=campaign_uuid,
        organization_id=current_user.organization_id
    )
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse.model_validate(campaign)


@router.patch(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Update campaign",
    description="Update a campaign's details"
)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a campaign:
    
    - **campaign_id**: UUID of the campaign
    - Only editable fields can be updated
    - Cannot edit campaigns in certain statuses (sending, sent)
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        campaign = await campaign_service.update_campaign(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            campaign_data=campaign_data
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{campaign_id}",
    response_model=MessageResponse,
    summary="Delete campaign",
    description="Delete a campaign"
)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a campaign:
    
    - **campaign_id**: UUID of the campaign
    - Cannot delete campaigns that are sending or sent
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        deleted = await campaign_service.delete_campaign(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return MessageResponse(message="Campaign deleted successfully")
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# CAMPAIGN OPERATIONS
# ============================================

@router.post(
    "/{campaign_id}/duplicate",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate campaign",
    description="Create a copy of an existing campaign"
)
async def duplicate_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Duplicate a campaign:
    
    - **campaign_id**: UUID of the campaign to duplicate
    - Creates a new campaign with same settings and objectives
    - New campaign will be in draft status
    - Name will be appended with " (Copy)"
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        duplicate = await campaign_service.duplicate_campaign(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            created_by=current_user.id
        )
        
        return CampaignResponse.model_validate(duplicate)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{campaign_id}/archive",
    response_model=CampaignResponse,
    summary="Archive campaign",
    description="Archive a campaign"
)
async def archive_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Archive a campaign:
    
    - **campaign_id**: UUID of the campaign
    - Sets campaign status to archived
    - Archived campaigns are hidden from default lists
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        campaign = await campaign_service.change_campaign_status(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            new_status=CampaignStatusEnum.ARCHIVED
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{campaign_id}/schedule",
    response_model=CampaignResponse,
    summary="Schedule campaign",
    description="Schedule a campaign for sending"
)
async def schedule_campaign(
    campaign_id: str,
    schedule_data: CampaignScheduleRequest,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule a campaign:
    
    - **campaign_id**: UUID of the campaign
    - **scheduled_at**: When to send the campaign (must be in future)
    - Campaign must be in appropriate status for scheduling
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        campaign = await campaign_service.schedule_campaign(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            scheduled_at=schedule_data.scheduled_at
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{campaign_id}/send",
    response_model=CampaignResponse,
    summary="Send campaign",
    description="Send campaign immediately"
)
async def send_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Send campaign immediately:
    
    - **campaign_id**: UUID of the campaign
    - Changes status to sending
    - Campaign must be ready to send
    - Actual email sending handled by background worker
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        campaign = await campaign_service.change_campaign_status(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            new_status=CampaignStatusEnum.SENDING
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # In production, trigger background job to send emails
        # background_tasks.add_task(send_campaign_emails, campaign.id)
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{campaign_id}/pause",
    response_model=CampaignResponse,
    summary="Pause campaign",
    description="Pause a sending or scheduled campaign"
)
async def pause_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Pause a campaign:
    
    - **campaign_id**: UUID of the campaign
    - Pauses sending or scheduled campaign
    - Can be resumed later
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        campaign = await campaign_service.change_campaign_status(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            new_status=CampaignStatusEnum.PAUSED
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{campaign_id}/resume",
    response_model=CampaignResponse,
    summary="Resume campaign",
    description="Resume a paused campaign"
)
async def resume_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Resume a paused campaign:
    
    - **campaign_id**: UUID of the campaign
    - Resumes a paused campaign to scheduled status
    - Can then be sent or rescheduled
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        campaign = await campaign_service.change_campaign_status(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            new_status=CampaignStatusEnum.SCHEDULED
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{campaign_id}/cancel",
    response_model=CampaignResponse,
    summary="Cancel campaign",
    description="Cancel a scheduled campaign"
)
async def cancel_campaign(
    campaign_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a scheduled campaign:
    
    - **campaign_id**: UUID of the campaign
    - Returns campaign to draft status
    - Clears scheduled time
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        # Get campaign first
        campaign = await campaign_service.get_campaign(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Clear scheduled time
        campaign.scheduled_at = None
        
        # Change to draft
        campaign = await campaign_service.change_campaign_status(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            new_status=CampaignStatusEnum.DRAFT
        )
        
        return CampaignResponse.model_validate(campaign)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# CAMPAIGN OBJECTIVES
# ============================================

@router.get(
    "/{campaign_id}/objectives",
    response_model=List[CampaignObjectiveResponse],
    summary="List campaign objectives",
    description="Get all objectives for a campaign"
)
async def list_objectives(
    campaign_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List campaign objectives:
    
    - **campaign_id**: UUID of the campaign
    
    Returns list of all objectives for the campaign.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    campaign = await campaign_service.get_campaign(
        campaign_id=campaign_uuid,
        organization_id=current_user.organization_id
    )
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return [CampaignObjectiveResponse.model_validate(obj) for obj in campaign.objectives]


@router.post(
    "/{campaign_id}/objectives",
    response_model=CampaignObjectiveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create campaign objective",
    description="Add a new objective to a campaign"
)
async def create_objective(
    campaign_id: str,
    objective_data: CampaignObjectiveCreate,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Create campaign objective:
    
    - **campaign_id**: UUID of the campaign
    - **objective_type**: Type of objective (primary/secondary)
    - **description**: Objective description
    - **kpi_name**: KPI to measure (open_rate, click_rate, conversion, etc.)
    - **target_value**: Target value for the KPI
    - **priority**: Priority level (1=highest)
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        objective = await campaign_service.create_objective(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            objective_data=objective_data
        )
        
        return CampaignObjectiveResponse.model_validate(objective)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch(
    "/{campaign_id}/objectives/{objective_id}",
    response_model=CampaignObjectiveResponse,
    summary="Update campaign objective",
    description="Update an existing campaign objective"
)
async def update_objective(
    campaign_id: str,
    objective_id: str,
    objective_data: CampaignObjectiveUpdate,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Update campaign objective:
    
    - **campaign_id**: UUID of the campaign
    - **objective_id**: UUID of the objective
    - Only provided fields will be updated
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
        objective_uuid = uuid.UUID(objective_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    objective = await campaign_service.update_objective(
        objective_id=objective_uuid,
        campaign_id=campaign_uuid,
        organization_id=current_user.organization_id,
        objective_data=objective_data
    )
    
    if not objective:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found"
        )
    
    return CampaignObjectiveResponse.model_validate(objective)


@router.delete(
    "/{campaign_id}/objectives/{objective_id}",
    response_model=MessageResponse,
    summary="Delete campaign objective",
    description="Delete a campaign objective"
)
async def delete_objective(
    campaign_id: str,
    objective_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete campaign objective:
    
    - **campaign_id**: UUID of the campaign
    - **objective_id**: UUID of the objective
    
    Requires member role or higher.
    """
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
        objective_uuid = uuid.UUID(objective_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    deleted = await campaign_service.delete_objective(
        objective_id=objective_uuid,
        campaign_id=campaign_uuid,
        organization_id=current_user.organization_id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Objective not found"
        )
    
    return MessageResponse(message="Objective deleted successfully")