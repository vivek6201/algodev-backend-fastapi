from logging.config import fileConfig
from alembic import context
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from alembic.autogenerate import renderers
from sqlalchemy.dialects.postgresql import ENUM

# NOW import app modules
from app.config.settings import settings
from app.common.db.config import engine
import sqlmodel
from app.modules.users.models.user import *
from app.modules.users.models.admin import *
from app.modules.jobs.models.jobs import *
from app.modules.education.blogs.models.blog import *
from app.modules.education.shared.model import *

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set your database URL from settings
config.set_main_option("sqlalchemy.url", settings.ASYNC_DATABASE_URL)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = sqlmodel.SQLModel.metadata

@renderers.dispatch_for(ENUM)
def render_enum(type_, autogen_context):
    return "sa.Enum(%s, name='%s', create_type=True, checkfirst=True)" % (
        ", ".join("'%s'" % e for e in type_.enums),
        type_.name
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()