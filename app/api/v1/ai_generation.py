"""
AI Generation endpoints for email content creation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import math

from core.database import get_db
from schemas.ai_generation import (
    AIGenerationRequest,
    AIGenerationResponse,
    AIRefinementRequest,
    SubjectLineVariantsRequest,
    SubjectLineVariantsResponse,
    AIGenerationJobList,
    AIJobStatus,
)
from schemas.auth import MessageResponse
from schemas.campaign import CampaignResponse
from services.ai_generation_service import AIGenerationService
from services.campaign_service import CampaignService
from api.deps import get_current_active_user, require_member
from models.user import User

# Import Celery tasks
from workers.ai_generation_tasks import (
    process_email_generation,
    process_email_refinement,
    process_subject_line_generation,
)

router = APIRouter(tags=["AI Generation"])


# ============================================
# EMAIL CONTENT GENERATION
# ============================================

@router.post(
    "/campaigns/{campaign_id}/generate",
    response_model=AIGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate email content",
    description="Generate email content using AI for a campaign (async operation)"
)
async def generate_email_content(
    campaign_id: str,
    generation_request: AIGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate email content using AI:
    
    - **campaign_id**: Campaign UUID
    - **user_prompt**: Your instructions for content generation
    - **generation_options**: Customization options (tone, length, etc.)
    - **context_override**: Additional context to supplement
    
    This is an **async operation** that returns immediately with a job_id.
    Poll the GET endpoint to check status and retrieve results.
    
    **Generation Options:**
    - **tone**: professional, friendly, formal, casual, urgent, enthusiastic
    - **length**: short (~100-150 words), medium (~200-300), long (~400-500)
    - **personalization_level**: low, medium, high
    - **variants_count**: 1-5 different versions
    - **temperature**: 0.0-1.0 (creativity level)
    
    Requires member role or higher.
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        # Create generation job
        job = await ai_service.create_generation_job(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            generation_request=generation_request
        )
        
        # Trigger background processing
        background_tasks.add_task(
            process_email_generation.delay,
            str(job.id)
        )
        
        # Update campaign status to generating
        campaign_service = CampaignService(db)
        from schemas.campaign import CampaignStatusEnum
        await campaign_service.change_campaign_status(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            new_status=CampaignStatusEnum.GENERATING
        )
        
        return AIGenerationResponse(
            id=job.id,
            campaign_id=campaign_id,
            status=AIJobStatus(job.status),
            job_type=job.job_type,
            estimated_completion_seconds=30,
            created_at=job.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create generation job: {str(e)}"
        )


@router.get(
    "/campaigns/{campaign_id}/generate/{job_id}",
    response_model=AIGenerationResponse,
    summary="Get generation job status",
    description="Get the status and results of an AI generation job"
)
async def get_generation_job_status(
    campaign_id: str,
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get generation job status and results:
    
    - **campaign_id**: Campaign UUID
    - **job_id**: Generation job UUID
    
    **Status values:**
    - **pending**: Job queued but not started
    - **processing**: AI is generating content
    - **completed**: Generation finished, results available
    - **failed**: Generation failed, check error_message
    - **cancelled**: Job was cancelled
    
    When status is 'completed', the `generated_content` field will contain:
    - **variants**: Array of generated email variants
    - Each variant includes: subject_line, preview_text, html_content, plain_text_content, confidence_score, reasoning
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    job = await ai_service.get_generation_job(
        job_id=job_uuid,
        campaign_id=campaign_uuid,
        organization_id=current_user.organization_id
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found"
        )
    
    return AIGenerationResponse(
        id=job.id,
        campaign_id=campaign_id,
        status=AIJobStatus(job.status),
        job_type=job.job_type,
        generated_content=job.generated_content,
        ai_model=job.ai_model,
        tokens_used=job.tokens_used,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at
    )


@router.get(
    "/campaigns/{campaign_id}/generate",
    response_model=AIGenerationJobList,
    summary="List generation jobs",
    description="List all generation jobs for a campaign"
)
async def list_generation_jobs(
    campaign_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List generation jobs for a campaign:
    
    - **campaign_id**: Campaign UUID
    - **page**: Page number
    - **per_page**: Items per page
    
    Returns paginated list of all generation jobs (initial, refinement, subject line tests, etc.)
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    jobs, total = await ai_service.list_generation_jobs(
        campaign_id=campaign_uuid,
        organization_id=current_user.organization_id,
        page=page,
        per_page=per_page
    )
    
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    return AIGenerationJobList(
        jobs=[AIGenerationResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.post(
    "/campaigns/{campaign_id}/generate/{job_id}/cancel",
    response_model=AIGenerationResponse,
    summary="Cancel generation job",
    description="Cancel a pending or processing generation job"
)
async def cancel_generation_job(
    campaign_id: str,
    job_id: str,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a generation job:
    
    - **campaign_id**: Campaign UUID
    - **job_id**: Generation job UUID
    
    Can only cancel jobs that are pending or processing.
    Requires member role or higher.
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    try:
        job = await ai_service.cancel_job(
            job_id=job_uuid,
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id
        )
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation job not found"
            )
        
        return AIGenerationResponse.model_validate(job)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# CREATE TEMPLATE FROM VARIANT
# ============================================

@router.post(
    "/campaigns/{campaign_id}/generate/{job_id}/create-template",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create template from variant",
    description="Create an email template from a generated variant"
)
async def create_template_from_variant(
    campaign_id: str,
    job_id: str,
    variant_id: int = Query(..., ge=1, description="Variant ID to use"),
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Create email template from a generated variant:
    
    - **campaign_id**: Campaign UUID
    - **job_id**: Generation job UUID
    - **variant_id**: Which variant to use (1-based index)
    
    Creates a new email template with the selected variant's content.
    Template will be in draft status and not set as current.
    
    Requires member role or higher.
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
        job_uuid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    try:
        template = await ai_service.create_template_from_variant(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            job_id=job_uuid,
            variant_id=variant_id,
            created_by=current_user.id
        )
        
        return MessageResponse(
            message=f"Template created successfully (ID: {template.id}, Version: {template.version})"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================
# CONTENT REFINEMENT
# ============================================

@router.post(
    "/campaigns/{campaign_id}/templates/{template_id}/refine",
    response_model=AIGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Refine email content",
    description="Refine existing email content with AI (async operation)"
)
async def refine_email_content(
    campaign_id: str,
    template_id: str,
    refinement_request: AIRefinementRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Refine existing email content:
    
    - **campaign_id**: Campaign UUID
    - **template_id**: Template UUID to refine
    - **refinement_instructions**: What to change/improve
    - **sections_to_change**: Optional list of specific sections (opening, body, cta, closing)
    - **generation_options**: Optional generation settings
    
    **Example refinement instructions:**
    - "Make the tone more urgent and add a sense of scarcity"
    - "Strengthen the CTA and add social proof"
    - "Simplify the language and reduce length by 30%"
    - "Add more specific statistics and customer testimonials"
    
    This is an async operation. Poll the GET endpoint for results.
    Requires member role or higher.
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
        template_uuid = uuid.UUID(template_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    # Update refinement request with template_id
    refinement_request.template_id = template_id
    
    try:
        job = await ai_service.refine_template(
            template_id=template_uuid,
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            refinement_request=refinement_request
        )
        
        # Trigger background processing
        background_tasks.add_task(
            process_email_refinement.delay,
            str(job.id)
        )
        
        return AIGenerationResponse(
            id=job.id,
            campaign_id=campaign_id,
            status=AIJobStatus(job.status),
            job_type=job.job_type,
            estimated_completion_seconds=25,
            created_at=job.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================
# SUBJECT LINE GENERATION
# ============================================

@router.post(
    "/campaigns/{campaign_id}/subject-lines",
    response_model=AIGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate subject line variants",
    description="Generate multiple subject line variants for A/B testing"
)
async def generate_subject_line_variants(
    campaign_id: str,
    request_data: SubjectLineVariantsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate subject line variants:
    
    - **campaign_id**: Campaign UUID
    - **template_id**: Optional template ID to base subject lines on
    - **email_content**: Optional email content (if no template_id)
    - **count**: Number of variants (1-10, default: 5)
    - **style**: Optional style preference
    
    **Style options:**
    - **benefit-driven**: Focus on value proposition
    - **question**: Engage with compelling questions
    - **urgency**: Create time-sensitive motivation
    - **curiosity**: Tease valuable information
    - **social-proof**: Reference success or popularity
    - **personalized**: Use personalization tokens
    
    Generates subject lines optimized for high open rates.
    This is an async operation.
    
    Requires member role or higher.
    """
    ai_service = AIGenerationService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        job = await ai_service.generate_subject_line_variants(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            request_data=request_data
        )
        
        # Trigger background processing
        background_tasks.add_task(
            process_subject_line_generation.delay,
            str(job.id)
        )
        
        return AIGenerationResponse(
            id=job.id,
            campaign_id=campaign_id,
            status=AIJobStatus(job.status),
            job_type=job.job_type,
            estimated_completion_seconds=15,
            created_at=job.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================
# REGENERATE WITH DIFFERENT OPTIONS
# ============================================

@router.post(
    "/campaigns/{campaign_id}/regenerate",
    response_model=AIGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regenerate email content",
    description="Regenerate email content with different options"
)
async def regenerate_email_content(
    campaign_id: str,
    generation_request: AIGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_member),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate email content:
    
    Similar to initial generation but increments the campaign's generation_iterations count.
    Use this when you want to try different approaches or options.
    
    - **campaign_id**: Campaign UUID
    - **user_prompt**: Updated instructions
    - **generation_options**: New generation options
    
    Requires member role or higher.
    """
    ai_service = AIGenerationService(db)
    campaign_service = CampaignService(db)
    
    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid campaign ID format"
        )
    
    try:
        # Get campaign and increment iterations
        campaign = await campaign_service.get_campaign(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id
        )
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        campaign.generation_iterations += 1
        await ai_service.db.commit()
        
        # Create generation job
        job = await ai_service.create_generation_job(
            campaign_id=campaign_uuid,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            generation_request=generation_request
        )
        
        # Trigger background processing
        background_tasks.add_task(
            process_email_generation.delay,
            str(job.id)
        )
        
        return AIGenerationResponse(
            id=job.id,
            campaign_id=campaign_id,
            status=AIJobStatus(job.status),
            job_type=job.job_type,
            estimated_completion_seconds=30,
            created_at=job.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )