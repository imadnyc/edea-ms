import json
import os
import databases
import pytest
import sqlalchemy
from httpx import AsyncClient

from .db import override_db, metadata
from .main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db(anyio_backend):
    engine = sqlalchemy.create_engine("sqlite:///.test.db")
    metadata.create_all(engine)
    override_db(databases.Database("sqlite:///.test.db"))
    yield
    os.remove(".test.db")


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.anyio
async def test_create_column_from_measurement_entry():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/projects/", json={"number": 1, "name": "Test Project"}
        )

    if response.status_code != 200:
        print(response.json())
        assert response.status_code == 200

    project = response.json()
    assert project["name"] == "Test Project"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/testruns/",
            json={
                "short_code": "ABCD",
                "dut_id": "1",
                "machine_hostname": "test",
                "user_name": "test",
                "test_name": "test",
                "project": project,
                "metadata": {},
            },
        )

    if response.status_code != 200:
        print(response.json())
        assert response.status_code == 200

    testrun = response.json()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/measurement_entries/",
            json={
                "sequence_number": 1,
                "testrun": {"id": testrun["id"]},
                "column": {"name": "test_col", "project": {"id": project["id"]}},
                "string_value": "test",
            },
        )

    if response.status_code != 200:
        print(json.dumps(response.json(), sort_keys=True, indent=4))
        assert response.status_code == 200

    assert response.json()["string_value"] == "test"
