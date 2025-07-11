from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# — import your SQLModel metadata and your engine or URL —
from sqlmodel import SQLModel
from app.models import User, JournalEntry   # <- imports your models so metadata has tables
from app.database import DATABASE_URL, engine # or import DATABASE_URL if you prefer

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# — override the URL in alembic.ini with the one from your .env/config —
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# tell Alembic about your metadata
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
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
    # use the same engine your app uses
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # so ALTER TYPE / column-type changes are detected
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()