import pytest
from httpx import AsyncClient

from ..db.models import JobState


@pytest.mark.anyio
async def test_root(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 307


@pytest.mark.anyio
async def test_export_db(client: AsyncClient) -> None:
    response = await client.get("/export/db")
    assert response.status_code == 200
    # assert len(response.content) >= 40000


@pytest.mark.anyio
async def test_jobqueue(client: AsyncClient) -> None:
    """
    Create, list, get, update and delete a job. Tests the whole workflow of jobs.
    :return:
    """
    r = await client.post(
        "/jobs/new",
        json={"function_call": "print", "parameters": {"hello": "world"}},
    )
    if r.status_code != 200:
        print(r.json())
    assert r.status_code == 200

    r = await client.get("/jobs/all")
    assert r.status_code == 200
    job_id = r.json()[-1]["id"]

    r = await client.get(f"/jobs/{job_id}")
    assert r.status_code == 200

    job_by_id = r.json()
    r = await client.get("/jobs/new")
    assert r.status_code == 200
    new_job = r.json()

    assert job_by_id["id"] == new_job["id"]
    assert int(new_job["state"]) == int(JobState.PENDING)

    new_job["worker"] = "test_worker"
    r = await client.put(f"/jobs/{job_id}", json=new_job)
    assert r.status_code == 200

    r = await client.delete(f"/jobs/{job_id}")
    assert r.status_code == 200
