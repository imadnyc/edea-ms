import databases
import pytest
import sqlalchemy
from httpx import AsyncClient

from .db import override_db, metadata
from .main import app

DATABASE_URL = "sqlite:///"

database = databases.Database(DATABASE_URL)
override_db(database)
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.anyio
async def test_create_project():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/projects/", json={"number": 1, "name": "Test Project"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Project"
