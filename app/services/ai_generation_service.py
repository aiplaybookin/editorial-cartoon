"""
AI Generation service using Anthropic Claude
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
import anthropic
from anthropic import AsyncAnthropic

from models.template import AIGenerationJob, EmailTemplate
from models.campaign import Campaign
from models.organization import CompanyProfile
from schemas.ai_generation import (
    AIGenerationRequest,
    AIRefinementRequest,
    SubjectLineVariantsRequest,
    AIJobStatus,
    AIJobType,
    EmailVariant,
)
from utils.prompts import (
    build_system_prompt,
    build_generation_prompt,
    build_refinement_prompt,
    build_subject_line_prompt,
    build_optimization_prompt,
)
from core.config import settings


class AIGenerationService:
    """Service for AI-powered email content generation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def create_generation_job(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        generation_request: AIGenerationRequest,
        job_type: AIJobType = AIJobType.INITIAL_GENERATION
    ) -> AIGenerationJob:
        """
        Create a new AI generation job
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            user_id: User UUID creating the job
            generation_request: Generation request data
            job_type: Type of generation job
            
        Returns:
            Created AI generation job
        """
        # Get campaign with objectives
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
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            raise ValueError("Campaign not found")
        
        # Get company profile
        profile_stmt = select(CompanyProfile).where(
            CompanyProfile.organization_id == organization_id
        )
        profile_result = await self.db.execute(profile_stmt)
        company_profile = profile_result.scalar_one_or_none()
        
        # Build context
        context = {
            "campaign": {
                "name": campaign.name,
                "description": campaign.description,
                "primary_goal": campaign.primary_goal,
                "target_audience_description": campaign.target_audience_description,
                "success_criteria": campaign.success_criteria,
                "objectives": [
                    {
                        "description": obj.description,
                        "kpi_name": obj.kpi_name,
                        "target_value": obj.target_value
                    }
                    for obj in campaign.objectives
                ]
            },
            "generation_options": generation_request.generation_options.model_dump(),
            "user_prompt": generation_request.user_prompt
        }
        
        if company_profile:
            context["company_profile"] = {
                "brand_voice": company_profile.brand_voice,
                "value_propositions": company_profile.value_propositions,
                "target_audience": company_profile.target_audience,
                "competitive_advantages": company_profile.competitive_advantages,
                "brand_guidelines": company_profile.brand_guidelines,
                "compliance_requirements": company_profile.compliance_requirements
            }
        
        if generation_request.context_override:
            context.update(generation_request.context_override)
        
        # Create job
        job = AIGenerationJob(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            job_type=job_type.value,
            status=AIJobStatus.PENDING.value,
            user_prompt=generation_request.user_prompt,
            context=context,
            created_by=user_id
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def process_generation_job(
        self,
        job_id: uuid.UUID
    ) -> AIGenerationJob:
        """
        Process an AI generation job
        
        Args:
            job_id: Job UUID
            
        Returns:
            Updated job with results
        """
        # Get job
        stmt = select(AIGenerationJob).where(AIGenerationJob.id == job_id)
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError("Job not found")
        
        # Update status to processing
        job.status = AIJobStatus.PROCESSING.value
        job.started_at = datetime.utcnow()
        await self.db.commit()
        
        try:
            # Get company profile from context
            company_profile = job.context.get('company_profile')
            
            # Build system prompt
            system_prompt = build_system_prompt(company_profile)
            
            # Build generation prompt based on job type
            if job.job_type == AIJobType.INITIAL_GENERATION.value:
                generation_prompt = build_generation_prompt(
                    user_prompt=job.user_prompt,
                    campaign_data=job.context.get('campaign', {}),
                    generation_options=job.context.get('generation_options', {}),
                    company_profile=company_profile
                )
            else:
                # Handle other job types
                generation_prompt = job.user_prompt
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=job.context.get('generation_options', {}).get('temperature', 0.7),
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": generation_prompt
                    }
                ]
            )
            
            # Extract content
            content_text = response.content[0].text
            
            # Parse JSON response
            try:
                generated_content = json.loads(content_text)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from markdown code block
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
                if json_match:
                    generated_content = json.loads(json_match.group(1))
                else:
                    # Fallback: wrap raw content
                    generated_content = {
                        "variants": [{
                            "variant_id": 1,
                            "subject_line": "Generated Email",
                            "preview_text": "",
                            "html_content": content_text,
                            "plain_text_content": content_text,
                            "confidence_score": 0.7,
                            "reasoning": "Raw AI output"
                        }]
                    }
            
            # Update job with results
            job.generated_content = generated_content
            job.ai_model = self.model
            job.tokens_used = response.usage.input_tokens + response.usage.output_tokens
            job.status = AIJobStatus.COMPLETED.value
            job.completed_at = datetime.utcnow()
            
            # Calculate confidence score (average of all variants)
            if generated_content.get('variants'):
                scores = [v.get('confidence_score', 0.7) for v in generated_content['variants']]
                job.confidence_score = sum(scores) / len(scores)
            
            await self.db.commit()
            await self.db.refresh(job)
            
            return job
            
        except Exception as e:
            # Update job with error
            job.status = AIJobStatus.FAILED.value
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(job)
            
            raise
    
    async def create_template_from_variant(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        job_id: uuid.UUID,
        variant_id: int,
        created_by: uuid.UUID
    ) -> EmailTemplate:
        """
        Create an email template from a generated variant
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            job_id: Generation job UUID
            variant_id: Which variant to use
            created_by: User creating the template
            
        Returns:
            Created email template
        """
        # Get job
        stmt = select(AIGenerationJob).where(
            and_(
                AIGenerationJob.id == job_id,
                AIGenerationJob.campaign_id == campaign_id
            )
        )
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job or job.status != AIJobStatus.COMPLETED.value:
            raise ValueError("Job not found or not completed")
        
        # Get variant
        variants = job.generated_content.get('variants', [])
        variant = next((v for v in variants if v['variant_id'] == variant_id), None)
        
        if not variant:
            raise ValueError(f"Variant {variant_id} not found")
        
        # Get current max version for campaign
        version_stmt = select(EmailTemplate).where(
            EmailTemplate.campaign_id == campaign_id
        ).order_by(EmailTemplate.version.desc()).limit(1)
        version_result = await self.db.execute(version_stmt)
        latest_template = version_result.scalar_one_or_none()
        
        new_version = (latest_template.version + 1) if latest_template else 1
        
        # Create template
        template = EmailTemplate(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            version=new_version,
            is_current=False,  # Don't set as current automatically
            subject_line=variant['subject_line'],
            preview_text=variant.get('preview_text'),
            html_content=variant['html_content'],
            plain_text_content=variant['plain_text_content'],
            generated_by='ai',
            ai_model_used=job.ai_model,
            generation_prompt=job.user_prompt,
            ai_metadata={
                "job_id": str(job_id),
                "variant_id": variant_id,
                "confidence_score": variant.get('confidence_score'),
                "reasoning": variant.get('reasoning'),
                "temperature": job.context.get('generation_options', {}).get('temperature'),
                "tokens_used": job.tokens_used
            },
            status='draft',
            created_by=created_by
        )
        
        self.db.add(template)
        await self.db.flush()  # Ensure template exists before linking
        
        # Link template to job
        job.template_id = template.id
        
        await self.db.commit()
        await self.db.refresh(template)
        
        return template
    
    async def refine_template(
        self,
        template_id: uuid.UUID,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        refinement_request: AIRefinementRequest
    ) -> AIGenerationJob:
        """
        Refine an existing email template
        
        Args:
            template_id: Template UUID
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            user_id: User UUID
            refinement_request: Refinement request data
            
        Returns:
            Created refinement job
        """
        # Get template
        stmt = select(EmailTemplate).where(
            and_(
                EmailTemplate.id == template_id,
                EmailTemplate.campaign_id == campaign_id
            )
        )
        result = await self.db.execute(stmt)
        template = result.scalar_one_or_none()
        
        if not template:
            raise ValueError("Template not found")
        
        # Build refinement context
        context = {
            "original_template": {
                "subject_line": template.subject_line,
                "preview_text": template.preview_text,
                "html_content": template.html_content,
                "plain_text_content": template.plain_text_content
            },
            "refinement_instructions": refinement_request.refinement_instructions,
            "sections_to_change": refinement_request.sections_to_change
        }
        
        if refinement_request.generation_options:
            context["generation_options"] = refinement_request.generation_options.model_dump()
        
        # Create job
        job = AIGenerationJob(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            job_type=AIJobType.REFINEMENT.value,
            status=AIJobStatus.PENDING.value,
            user_prompt=refinement_request.refinement_instructions,
            context=context,
            created_by=user_id
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def process_refinement_job(
        self,
        job_id: uuid.UUID
    ) -> AIGenerationJob:
        """
        Process a refinement job
        
        Args:
            job_id: Job UUID
            
        Returns:
            Updated job with results
        """
        # Get job
        stmt = select(AIGenerationJob).where(AIGenerationJob.id == job_id)
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError("Job not found")
        
        # Update status
        job.status = AIJobStatus.PROCESSING.value
        job.started_at = datetime.utcnow()
        await self.db.commit()
        
        try:
            # Build refinement prompt
            refinement_prompt = build_refinement_prompt(
                original_content=job.context.get('original_template', {}),
                refinement_instructions=job.user_prompt,
                sections_to_change=job.context.get('sections_to_change')
            )
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=job.context.get('generation_options', {}).get('temperature', 0.7),
                messages=[
                    {
                        "role": "user",
                        "content": refinement_prompt
                    }
                ]
            )
            
            # Extract and parse content
            content_text = response.content[0].text
            
            try:
                generated_content = json.loads(content_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
                if json_match:
                    generated_content = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse AI response as JSON")
            
            # Wrap in variants format for consistency
            if 'variants' not in generated_content:
                generated_content = {
                    "variants": [{
                        "variant_id": 1,
                        "subject_line": generated_content.get('subject_line', ''),
                        "preview_text": generated_content.get('preview_text', ''),
                        "html_content": generated_content.get('html_content', ''),
                        "plain_text_content": generated_content.get('plain_text_content', ''),
                        "confidence_score": generated_content.get('confidence_score', 0.85),
                        "reasoning": generated_content.get('changes_made', '')
                    }]
                }
            
            # Update job
            job.generated_content = generated_content
            job.ai_model = self.model
            job.tokens_used = response.usage.input_tokens + response.usage.output_tokens
            job.confidence_score = generated_content['variants'][0].get('confidence_score', 0.85)
            job.status = AIJobStatus.COMPLETED.value
            job.completed_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(job)
            
            return job
            
        except Exception as e:
            job.status = AIJobStatus.FAILED.value
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            await self.db.commit()
            raise
    
    async def generate_subject_line_variants(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        request_data: SubjectLineVariantsRequest
    ) -> AIGenerationJob:
        """
        Generate subject line variants
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            user_id: User UUID
            request_data: Subject line request data
            
        Returns:
            Created generation job
        """
        # Get email content if template_id provided
        email_content = None
        if request_data.template_id:
            template_uuid = uuid.UUID(request_data.template_id)
            stmt = select(EmailTemplate).where(EmailTemplate.id == template_uuid)
            result = await self.db.execute(stmt)
            template = result.scalar_one_or_none()
            
            if template:
                email_content = template.html_content
        elif request_data.email_content:
            email_content = request_data.email_content
        
        # Get campaign context
        stmt = select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.organization_id == organization_id
            )
        )
        result = await self.db.execute(stmt)
        campaign = result.scalar_one_or_none()
        
        campaign_context = None
        if campaign:
            campaign_context = {
                "primary_goal": campaign.primary_goal,
                "target_audience_description": campaign.target_audience_description
            }
        
        # Build context
        context = {
            "email_content": email_content,
            "campaign_context": campaign_context,
            "count": request_data.count,
            "style": request_data.style
        }
        
        # Create job
        job = AIGenerationJob(
            id=uuid.uuid4(),
            campaign_id=campaign_id,
            job_type=AIJobType.SUBJECT_LINE_TEST.value,
            status=AIJobStatus.PENDING.value,
            user_prompt=f"Generate {request_data.count} subject line variants",
            context=context,
            created_by=user_id
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def process_subject_line_job(
        self,
        job_id: uuid.UUID
    ) -> AIGenerationJob:
        """
        Process subject line generation job
        
        Args:
            job_id: Job UUID
            
        Returns:
            Updated job with results
        """
        # Get job
        stmt = select(AIGenerationJob).where(AIGenerationJob.id == job_id)
        result = await self.db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError("Job not found")
        
        # Update status
        job.status = AIJobStatus.PROCESSING.value
        job.started_at = datetime.utcnow()
        await self.db.commit()
        
        try:
            # Build prompt
            subject_line_prompt = build_subject_line_prompt(
                email_content=job.context.get('email_content'),
                campaign_context=job.context.get('campaign_context'),
                count=job.context.get('count', 5),
                style=job.context.get('style')
            )
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.8,  # Higher creativity for subject lines
                messages=[
                    {
                        "role": "user",
                        "content": subject_line_prompt
                    }
                ]
            )
            
            # Parse response
            content_text = response.content[0].text
            
            try:
                generated_content = json.loads(content_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content_text, re.DOTALL)
                if json_match:
                    generated_content = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse AI response")
            
            # Update job
            job.generated_content = generated_content
            job.ai_model = self.model
            job.tokens_used = response.usage.input_tokens + response.usage.output_tokens
            job.status = AIJobStatus.COMPLETED.value
            job.completed_at = datetime.utcnow()
            
            # Calculate average confidence
            if generated_content.get('variants'):
                scores = [v.get('confidence_score', 0.8) for v in generated_content['variants']]
                job.confidence_score = sum(scores) / len(scores)
            
            await self.db.commit()
            await self.db.refresh(job)
            
            return job
            
        except Exception as e:
            job.status = AIJobStatus.FAILED.value
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            await self.db.commit()
            raise
    
    async def get_generation_job(
        self,
        job_id: uuid.UUID,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> Optional[AIGenerationJob]:
        """
        Get a generation job
        
        Args:
            job_id: Job UUID
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            
        Returns:
            Job or None
        """
        # Verify campaign belongs to organization
        campaign_stmt = select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.organization_id == organization_id
            )
        )
        campaign_result = await self.db.execute(campaign_stmt)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            return None
        
        # Get job
        stmt = select(AIGenerationJob).where(
            and_(
                AIGenerationJob.id == job_id,
                AIGenerationJob.campaign_id == campaign_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_generation_jobs(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[AIGenerationJob], int]:
        """
        List generation jobs for a campaign
        
        Args:
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (jobs list, total count)
        """
        # Verify campaign
        campaign_stmt = select(Campaign).where(
            and_(
                Campaign.id == campaign_id,
                Campaign.organization_id == organization_id
            )
        )
        campaign_result = await self.db.execute(campaign_stmt)
        campaign = campaign_result.scalar_one_or_none()
        
        if not campaign:
            return [], 0
        
        # Count query
        from sqlalchemy import func
        count_query = select(func.count()).select_from(AIGenerationJob).where(
            AIGenerationJob.campaign_id == campaign_id
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get jobs
        offset = (page - 1) * per_page
        stmt = (
            select(AIGenerationJob)
            .where(AIGenerationJob.campaign_id == campaign_id)
            .order_by(AIGenerationJob.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()
        
        return list(jobs), total
    
    async def cancel_job(
        self,
        job_id: uuid.UUID,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID
    ) -> Optional[AIGenerationJob]:
        """
        Cancel a pending or processing job
        
        Args:
            job_id: Job UUID
            campaign_id: Campaign UUID
            organization_id: Organization UUID
            
        Returns:
            Cancelled job or None
        """
        job = await self.get_generation_job(job_id, campaign_id, organization_id)
        
        if not job:
            return None
        
        if job.status not in [AIJobStatus.PENDING.value, AIJobStatus.PROCESSING.value]:
            raise ValueError("Can only cancel pending or processing jobs")
        
        job.status = AIJobStatus.CANCELLED.value
        job.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(job)
        
        return job