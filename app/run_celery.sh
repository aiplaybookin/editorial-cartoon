#!/bin/bash

# Start Celery worker for AI generation tasks
celery -A workers.celery_app worker \
    --loglevel=info \
    --queues=ai_generation \
    --concurrency=2 \
    --pool=solo