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
