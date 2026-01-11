# AI Campaign Manager

An AI-powered email campaign management platform that helps marketers:
- Create strategic campaign plans
- Define and understand target audiences
- Generate AI-powered email content using Claude
- Measure campaign performance to drive successful outcomes

## Prerequisites

- Python 3.12+
- PostgreSQL (with asyncpg support)
- Redis Server
- Anthropic API Key ([Get one here](https://console.anthropic.com/))

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set the required values:

```bash
# REQUIRED: Set your Anthropic API key
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Update database connection
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/email_campaign_db

# Generate a new secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Configure other settings as needed
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 4. Start Redis Server

```bash
# On macOS (using Homebrew)
brew install redis
brew services start redis

# On Linux (using apt)
sudo apt-get install redis-server
sudo systemctl start redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### 5. Start the Application

```bash
# Terminal 1: Start FastAPI server
uv run app/main.py

# Terminal 2: Start Celery worker
./run_celery.sh
# Or manually:
CELERY_WORKER=true PYTHONPATH=app uv run celery -A workers.celery_app worker --loglevel=info --queues=ai_generation --concurrency=2 --pool=solo
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Troubleshooting

### AI Generation Getting Stuck in Pending State

If AI generation tasks are stuck with "pending" status:

1. **Check Celery Worker is Running**: Look for logs in the terminal running Celery
2. **Verify API Key**: Ensure `ANTHROPIC_API_KEY` is set correctly in `.env`
3. **Check Redis Connection**: Run `redis-cli ping` to verify Redis is accessible
4. **Review Celery Logs**: Look for authentication or connection errors

Common errors:
- `"Could not resolve authentication method"` → API key not set in `.env`
- `RuntimeError: Event loop is closed` → Fixed in recent updates
- Connection refused to Redis → Start Redis server

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql -h localhost -U user -d email_campaign_db

# Verify DATABASE_URL format
# Correct: postgresql+asyncpg://user:password@localhost:5432/dbname
```

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
├── main.py (update)
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
├── main.py (update)
├── run_celery.sh (new)
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
├── tests/
│   └── integration.py (new)
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

