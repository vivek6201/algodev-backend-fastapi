#!/bin/sh
set -e

# Run migrations if RUN_MIGRATIONS is set to true
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running Alembic migrations..."
    
    uv run alembic upgrade head

    echo "✅ Migrations completed successfully"
fi

# Run admin creation script if CREATE_DEV_ADMIN is set to true
if [ "$CREATE_DEV_ADMIN" = "true" ]; then
    echo "Running admin creation script..."
    
    uv run python -m app.common.db.scripts.initial_entry

    echo "✅ Admin creation script completed"
fi

# Execute the main command (CMD from Dockerfile)
exec "$@"