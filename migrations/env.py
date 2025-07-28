import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Import your Flask app's models and app factory
import os
from flask import Flask, current_app
from app import create_app  # Assuming create_app is in app/__init__.py
from app.models import db, User, InterviewExperience, ResetToken # Import models for target_metadata

# Use the MetaData from your SQLAlchemy db instance
target_metadata = db.metadata

# === MODIFIED SECTION FOR DATABASE URL HANDLING ===
# Get the database URL from Render's environment variable if available.
# This is CRUCIAL for builds on Render.
render_db_url = os.environ.get("DATABASE_URL")

if render_db_url:
    # Render's DATABASE_URL usually starts with 'postgres://', but SQLAlchemy prefers 'postgresql://'
    if render_db_url.startswith("postgres://"):
        render_db_url = render_db_url.replace("postgres://", "postgresql://", 1)
    config.set_main_option("sqlalchemy.url", render_db_url)
else:
    # If DATABASE_URL is not set (e.g., during local 'flask db' commands),
    # then load it from your Flask app's config.
    # This requires running within the Flask app context.
    app = create_app()
    with app.app_context():
        # Ensure Flask-SQLAlchemy has initialized the URI from your Config class
        if current_app.config.get('SQLALCHEMY_DATABASE_URI'):
            config.set_main_option(
                "sqlalchemy.url", current_app.config['SQLALCHEMY_DATABASE_URI']
            )
        else:
            # This should ideally not be hit if your config is set up correctly
            raise Exception(
                "No DATABASE_URL environment variable set and "
                "SQLALCHEMY_DATABASE_URI not found in Flask app config."
            )
# === END MODIFIED SECTION ===


# other values from the config, defined by the needs of env.py,
# can be acquired here and passed to the migration context.
# for example, context.config['my_setting']
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here send literal SQL to the
    use in the form of a string.
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
