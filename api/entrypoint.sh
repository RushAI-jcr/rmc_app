#!/bin/sh
set -e

# Run migrations before starting the app
echo "Running database migrations..."
alembic -c api/alembic.ini upgrade head

# Execute the CMD
exec "$@"
