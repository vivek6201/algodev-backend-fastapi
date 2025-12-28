from logging.config import fileConfig
from alembic import context
import asyncio

import sqlmodel
from sqlalchemy.dialects.postgresql import ENUM
from alembic.autogenerate import renderers

from app.config.settings import settings
from app.common.db.config import engine
from app.common.db.models import *  # noqa

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)


def get_sync_url():
    return settings.ASYNC_DATABASE_URL.replace("+asyncpg", "")


config.set_main_option("sqlalchemy.url", get_sync_url())

target_metadata = sqlmodel.SQLModel.metadata


@renderers.dispatch_for(ENUM)
def render_enum(type_, autogen_context):
    autogen_context.imports.add("import sqlalchemy as sa")
    return (
        "sa.Enum(%s, name='%s', create_type=True)"
        % (
            ", ".join(repr(e) for e in type_.enums),
            type_.name,
        )
    )


def run_migrations_offline():
    context.configure(
        url=get_sync_url(),
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


async def run_async_migrations():
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
