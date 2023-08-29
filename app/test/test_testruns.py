import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_crud_testrun(client: AsyncClient) -> None:
    h = {"X-Webauth-User": "user-1"}
    p1 = {
        "short_code": "TLA_P1",
        "name": "project with groups",
        "groups": ["group_a", "group_b"],
    }

    r = await client.post("/projects", headers=h, json=p1)
    assert r.status_code == 200

    p = r.json()

    r = await client.post(
        "/testruns",
        headers=h,
        json={
            "project_id": p["id"],
            "dut_id": "device_1",
            "machine_hostname": "test",
            "user_name": "user-1",
            "test_name": "unit-test",
            "data": {"a": "b"},
        },
    )

    assert r.status_code == 201
    tr = r.json()

    url = f"/testruns/{tr['id']}"

    # update the name of the test machine
    tr["machine_hostname"] = "other-machine"
    r = await client.put(url, headers=h, json=tr)
    assert r.status_code == 200

    r = await client.get(url, headers=h)
    assert r.status_code == 200

    tr = r.json()

    assert tr["machine_hostname"] == "other-machine"

    r = await client.delete(url, headers=h)
    assert r.status_code == 200

    # verify it's gone now
    r = await client.get(url, headers=h)
    assert r.status_code == 404
