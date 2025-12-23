#!/bin/sh
set -e

# Run migrations if RUN_MIGRATIONS is set to true
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running Alembic migrations..."
    
    /app/.venv/bin/alembic upgrade head

    echo "✅ Migrations completed successfully"
fi

# Execute the main command (CMD from Dockerfile)
exec "$@"