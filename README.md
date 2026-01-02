# AI Campaign 

Vision: <Write a vision for the AI Campaign>


- Creating strategic plans
- Defining target audiences
- Developing creative content
- Measuring campaign performance to drive successful outcomes

## Step 1: Database Model 
- app/models
- app/core/database.py
- alembic/*

Commands:
```
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

1. Tables are created in the database
2. alembic/versions/95d0f8a235fe_initial_schema.py is created

## Step 2: Auth Service and API
- /schemas/auth.py
- /services/auth_service.py
- /api/v1/auth.py
- /api/deps.py
- /core/config.py
- /core/security.py
- main.py

Run the app
```
uv run app/main.py
```

## Step 3: Campaign Service and API

CRUD operations, campaign management, and objectives handling. To do this, we need to create the following files:
```
app/
├── schemas/
│   ├── __init__.py (update)
│   ├── auth.py (already created)
│   └── campaign.py (new)
├── services/
│   ├── __init__.py (update)
│   ├── auth_service.py (already created)
│   └── campaign_service.py (new)
├── api/
│   └── v1/
│       ├── __init__.py 
│       ├── auth.py (already created)
│       └── campaigns.py (new)
```

## Step 4: AI Generation Service and API

To do this, we need to create the following files:

```
app/
├── schemas/
│   ├── __init__.py
│   ├── auth.py (existing)
│   ├── campaign.py (existing)
│   └── ai_generation.py (new)
├── services/
│   ├── __init__.py
│   ├── auth_service.py (existing)
│   ├── campaign_service.py (existing)
│   └── ai_generation_service.py (new)
├── workers/
│   ├── __init__.py
│   ├── celery_app.py (new)
│   └── ai_generation_tasks.py (new)
├── utils/
│   ├── __init__.py
│   └── prompts.py (new)
└── api/
    └── v1/
        ├── __init__.py
        ├── auth.py (existing)
        ├── campaigns.py (existing)
        └── ai_generation.py (new)
```
#### Celery
#### Redis
Install the actual Redis Server application for the client to connect to.
1. Install Redis Server using Homebrew:
```brew install redis```
2. Start the Server
```brew services start redis```
3. Run Celery again
```./run_celery.sh```

```
# 1. Navigate to the script's directory (if not already there)
cd /path/to/your/project

# 2. Activate your virtual environment (if using one)
source venv/bin/activate # Or wherever your venv is located

# 3. Make the script executable
chmod +x run_celery.sh

# 4. Run the script
./run_celery.sh
```

CELERY_WORKER=true PYTHONPATH=app uv run celery -A workers.celery_app worker --loglevel=info --queues=ai_generation --concurrency=2 --pool=solo


ps aux | grep python

