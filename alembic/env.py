"""Alembic environment.

Lê ``DATABASE_URL`` do ambiente (em vez do ``alembic.ini``) e usa o
``MetaData`` do projeto como alvo para ``--autogenerate``.

Quando ``core/config.py`` (pydantic-settings) for criado, esta leitura
direta de ``os.environ`` deve ser substituída por ``settings.database_url``.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from news_sentiment.infrastructure.db.base import Base

# Alembic Config object — acesso aos valores do alembic.ini.
config = context.config

# Injeta a URL do banco vinda do ambiente.
database_url = os.environ.get("DATABASE_URL")
if database_url is None:
    raise RuntimeError(
        "DATABASE_URL não está definida. Configure a variável de ambiente antes de rodar o Alembic."
    )
config.set_main_option("sqlalchemy.url", database_url)

# Configura logging conforme o ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData alvo para autogenerate.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Roda migrations em modo 'offline' (sem engine, só emite SQL)."""
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
    """Roda migrations em modo 'online' (conecta no banco)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
