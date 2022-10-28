import json
import os
from typing import AsyncIterable

import databases
import pytest
import sqlalchemy
from httpx import AsyncClient

from ..db import override_db, metadata
from ..db.models import JobState
from ..main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db(anyio_backend: str) -> AsyncIterable[None]:
    engine = sqlalchemy.create_engine("sqlite:///.test.db")
    metadata.create_all(engine)
    override_db(databases.Database("sqlite:///.test.db"))
    yield
    os.remove(".test.db")


@pytest.mark.anyio
async def test_root() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 307


@pytest.mark.anyio
async def test_create_column_from_measurement_entry() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/projects", json={"number": "X1234", "name": "Test Project"}
        )

    if response.status_code != 200:
        print(response.json())
        assert response.status_code == 200

    project = response.json()
    assert project["name"] == "Test Project"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/testruns",
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
            "/measurement_entries",
            json={
                "sequence_number": 1,
                "testrun": {"id": testrun["id"]},
                "column": {"name": "test_col", "project_id": project["id"]},
                "string_value": "test",
            },
        )

    if response.status_code != 200:
        print(json.dumps(response.json(), sort_keys=True, indent=4))
        assert response.status_code == 200

    assert response.json()["string_value"] == "test"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/measurement_entries/batch", json={
            "sequence_number": 1,
            "testrun_id": testrun["id"],
            "payload": {
                "1": {"column": {"name": "test_col", "project_id": project["id"]}, "test_value": "abcd"},
                "2": {"column": {"name": "test_col", "project_id": project["id"]}, "test_value": "efgh"},
            }
        })

    if response.status_code != 201:
        print(response.text)
        assert response.status_code == 201


@pytest.mark.anyio
async def test_export_db() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/export/db")
    assert response.status_code == 200
    # assert len(response.content) >= 40000


@pytest.mark.anyio
async def test_jobqueue() -> None:
    """
    Create, list, get, update and delete a job. Tests the whole workflow of jobs.
    :return:
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/jobs/new", json={"function_call": "print", "parameters": {"hello": "world"}})
        assert r.status_code == 200

        r = await ac.get("/jobs/all")
        assert r.status_code == 200
        job_id = r.json()[-1]["id"]

        r = await ac.get(f"/jobs/{job_id}")
        assert r.status_code == 200

        job_by_id = r.json()
        r = await ac.get("/jobs/new")
        assert r.status_code == 200
        new_job = r.json()

        assert job_by_id["id"] == new_job["id"]
        assert int(new_job["state"]) == int(JobState.PENDING)

        new_job["worker"] = "test_worker"
        r = await ac.put(f"/jobs/{job_id}", json=new_job)
        assert r.status_code == 200

        r = await ac.delete(f"/jobs/{job_id}")
        assert r.status_code == 200
