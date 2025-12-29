# AI Campaign 

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

## Step 2: 
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