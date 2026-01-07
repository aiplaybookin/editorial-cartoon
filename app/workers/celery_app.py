"""
Celery configuration for async tasks
"""
import os
from pathlib import Path
from celery import Celery

# Ensure .env is loaded before importing settings
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from core.config import settings

# Create Celery app
celery_app = Celery(
    "email_campaign_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.ai_generation_tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=270,  # 4.5 minutes
)

# Optional: Configure task routes
# Optional: Configure task routes
celery_app.conf.task_routes = {
    "process_email_generation": {"queue": "ai_generation"},
    "process_email_refinement": {"queue": "ai_generation"},
    "process_subject_line_generation": {"queue": "ai_generation"},
}