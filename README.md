# AI Campaign 

# Step 1: Database Model 
app/models
app/core/database.py
alembic/*

Commands:
```
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

1. Tables are created in the database
2. alembic/versions/95d0f8a235fe_initial_schema.py is created

# Step 2: 