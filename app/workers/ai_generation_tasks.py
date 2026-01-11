"""
Celery tasks for AI generation
"""
import asyncio
from celery import Task
from workers.celery_app import celery_app
from core.database import AsyncSessionLocal
from services.ai_generation_service import AIGenerationService
import uuid


class AsyncTask(Task):
    """Base task with async support - uses existing event loop or creates a new one"""

    def __call__(self, *args, **kwargs):
        # Check if there's an existing event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
            # Use existing loop
            return loop.run_until_complete(self.run(*args, **kwargs))
        except RuntimeError:
            # No event loop exists or it's closed, create a new one
            return asyncio.run(self.run(*args, **kwargs))

    async def run(self, *args, **kwargs):
        raise NotImplementedError()


@celery_app.task(base=AsyncTask, bind=True, name="process_email_generation")
async def process_email_generation(self, job_id: str):
    """
    Process email content generation job
    
    Args:
        job_id: UUID of the generation job
    """
    async with AsyncSessionLocal() as db:
        ai_service = AIGenerationService(db)
        
        try:
            job = await ai_service.process_generation_job(uuid.UUID(job_id))
            return {
                "status": "completed",
                "job_id": str(job.id),
                "variants_count": len(job.generated_content.get('variants', []))
            }
        except Exception as e:
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e)
            }


@celery_app.task(base=AsyncTask, bind=True, name="process_email_refinement")
async def process_email_refinement(self, job_id: str):
    """
    Process email content refinement job
    
    Args:
        job_id: UUID of the refinement job
    """
    async with AsyncSessionLocal() as db:
        ai_service = AIGenerationService(db)
        
        try:
            job = await ai_service.process_refinement_job(uuid.UUID(job_id))
            return {
                "status": "completed",
                "job_id": str(job.id)
            }
        except Exception as e:
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e)
            }


@celery_app.task(base=AsyncTask, bind=True, name="process_subject_line_generation")
async def process_subject_line_generation(self, job_id: str):
    """
    Process subject line generation job
    
    Args:
        job_id: UUID of the subject line job
    """
    async with AsyncSessionLocal() as db:
        ai_service = AIGenerationService(db)
        
        try:
            job = await ai_service.process_subject_line_job(uuid.UUID(job_id))
            return {
                "status": "completed",
                "job_id": str(job.id),
                "variants_count": len(job.generated_content.get('variants', []))
            }
        except Exception as e:
            return {
                "status": "failed",
                "job_id": job_id,
                "error": str(e)
            }