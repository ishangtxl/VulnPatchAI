#!/bin/bash

echo "Starting VulnPatch AI Backend..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
python -c "
import time
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os

database_url = os.getenv('DATABASE_URL', 'postgresql://vulnpatch:vulnpatch@postgres:5432/vulnpatch_db')
engine = create_engine(database_url)

max_retries = 30
retry_delay = 2

for attempt in range(max_retries):
    try:
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        print('Database is ready!')
        break
    except OperationalError as e:
        if attempt < max_retries - 1:
            print(f'Database not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay} seconds...')
            time.sleep(retry_delay)
        else:
            print('ERROR: Could not connect to database after 30 attempts')
            sys.exit(1)
"

# Run database migrations
echo "Running database migrations..."
python create_migration.py

# Create demo user
echo "Creating demo user..."
python create_demo_user.py

# Start the application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload