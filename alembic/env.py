import asyncio
from logging.config import fileConfig
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Read settings YAML file
import os  # noqa: E402

from yaml import safe_load  # noqa: E402


def _is_inside_docker() -> bool:
    return Path("/.dockerenv").exists()


def _replace_hostname_with_localhost(url: str) -> str:
    parts = urlsplit(url)
    if not parts.netloc:
        return url
    userinfo = ""
    host_port = parts.netloc
    if "@" in parts.netloc:
        userinfo, host_port = parts.netloc.rsplit("@", 1)
    if host_port == "db" or host_port.startswith("db:"):
        host_port = host_port.replace("db", "localhost", 1)
        netloc = f"{userinfo}@{host_port}" if userinfo else host_port
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    return url


app_settings_path = Path(os.getenv("SETTINGS_PATH", "settings.yaml"))
app_settings = safe_load(app_settings_path.read_text())

# Prefer explicit env override for migrations, then fallback to app settings.
db_url = os.getenv("ALEMBIC_DB_URL") or os.getenv("DATABASE_URL") or app_settings["db_url"]

# Allow local migrations when settings use docker-compose hostname "db".
if not _is_inside_docker():
    db_url = _replace_hostname_with_localhost(db_url)

config.set_main_option("sqlalchemy.url", db_url)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from src.db.schema import metadata  # noqa: E402

target_metadata = metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)


# https://stackoverflow.com/a/71212675/19566814
# almost identical to Flask-Migrate (Thanks miguel!)
# this callback is used to prevent an auto-migration from being generated
# when there are no changes to the schema


def process_revision_directives(context, revision, directives):
    if config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []
            print("No changes in schema detected.")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
