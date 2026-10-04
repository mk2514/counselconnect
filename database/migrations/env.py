"""
Alembic migration environment configuration.

This env.py adds the API app to the Python path so that
SQLAlchemy models can be imported for autogenerate support.
"""

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool  # pyright: ignore[reportMissingImports]
from alembic import context  # pyright: ignore[reportMissingImports]

# Add the api app to the path so models can be imported
api_path = str(Path(__file__).resolve().parents[2] / "apps" / "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)

from app.models import Base  # type: ignore # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from app.config import settings  # type: ignore # pyright: ignore[reportMissingImports, reportMissingModuleSource]

config = context.config

# Override sqlalchemy.url from environment
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
