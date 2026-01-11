"""
Celery configuration for async tasks
"""
from celery import Celery
from pathlib import Path
from dotenv import load_dotenv
import os

# Explicitly load .env file before importing settings
# This ensures environment variables are available when Celery worker starts
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment variables from {env_path}")
else:
    print(f"⚠ Warning: .env file not found at {env_path}")

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