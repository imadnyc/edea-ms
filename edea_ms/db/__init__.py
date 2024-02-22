import contextlib
import os
import sys

from alembic.command import upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_engine_from_config,
    async_sessionmaker,
    create_async_engine,
)

dbfile = "edea-ms.sqlite"
default_db = f"sqlite+aiosqlite:///{dbfile}"
DATABASE_URL = os.getenv("DATABASE_URL", default_db)

if "pytest" in sys.modules:
    DATABASE_URL = "sqlite+aiosqlite:///test.db"

print(f"using DB from {DATABASE_URL}")
engine = create_async_engine(DATABASE_URL)


def override_db(db: AsyncEngine) -> None:
    global engine
    engine = db


def async_session() -> AsyncSession:
    return async_sessionmaker(engine, expire_on_commit=False)()


async def run_migrations() -> None:
    """
    run_migrations checks if there are pending migrations and performs them if necessary
    """
    is_latest = False
    config = Config()
    config.set_main_option("script_location", "edea_ms.db:alembic")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
    )

    directory = ScriptDirectory.from_config(config)
    async with connectable.connect() as connection:
        context = await connection.run_sync(MigrationContext.configure)
        # in the rather complex testcase of running a uvicorn server while running playwright all in pytest there's some
        # hidden issues which we need to investigate sometime, for now just suppress the exception.
        with contextlib.suppress(MissingGreenlet):
            is_latest = set(context.get_current_heads()) == set(directory.get_heads())
    if not is_latest:
        upgrade(config, "head")
