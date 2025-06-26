import asyncio
import os
import sys
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool

# Импортируем async_engine_from_config для асинхронных миграций
from sqlalchemy.ext.asyncio import async_engine_from_config

# Это наш базовый объект MetaData из src.models.
# Make sure to import your Base from src.models
# Добавляем корневую директорию проекта в sys.path
# Add the project root to sys.path so Alembic can find your module with models
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.models import Base

# Load environment variables from .env file
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# fileConfig(config.config_file_name) # You might want to uncomment this for file logging

# Set the SQLAlchemy URL from environment variable
# This is crucial for Alembic to know where to connect
config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL"))


# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an actual DBAPI connection.

    By doing this, we can skip connecting to the database
    and just output the SQL statements to stdout.
    """
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
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Run migrations in 'async' mode."""
    # This line tells Alembic to use an asynchronous engine.
    # It reads connection details from the config (which gets them from DATABASE_URL)
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Here, we run the asynchronous migrations
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
