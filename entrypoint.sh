#!/bin/bash

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Uvicorn server on port ${PORT:-8000}..."
exec uvicorn app.app:app --host 0.0.0.0 --port ${PORT:-8000}