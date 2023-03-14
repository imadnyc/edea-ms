import asyncio
from typing import Any, AsyncIterable

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from ..db import override_db, DATABASE_URL
from ..db.models import Model
from ..main import app


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
def event_loop() -> Any:
    """
    Overrides pytest default function scoped event loop.
    This is needed to set up the DB once per session.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="module")
async def setup_db() -> AsyncIterable[None]:
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    override_db(engine)
    yield


@pytest.fixture(scope="module")
async def client() -> AsyncIterable[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
