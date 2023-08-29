import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_config_var(client: AsyncClient) -> None:
    r = await client.post("/config", json={"key": "a", "value": "b"})
    assert r.status_code == 201


@pytest.mark.anyio
async def test_get_config_var(client: AsyncClient) -> None:
    r = await client.get("/config/a")
    assert r.status_code == 200
    # return value is valid json
    assert r.text == '"b"'


@pytest.mark.anyio
async def test_get_config_var_not_exist(client: AsyncClient) -> None:
    r = await client.get("/config/b")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_update_config_var(client: AsyncClient) -> None:
    r = await client.post("/config", json={"key": "c", "value": "c"})
    assert r.status_code == 201

    r = await client.put("/config", json={"key": "c", "value": "d"})
    assert r.status_code == 200


@pytest.mark.anyio
async def test_update_config_var_not_exist(client: AsyncClient) -> None:
    r = await client.put("/config", json={"key": "x", "value": "y"})
    assert r.status_code == 404


@pytest.mark.anyio
async def test_get_all_vars(client: AsyncClient) -> None:
    r = await client.get("/config")
    assert r.status_code == 200
    # return value is valid json
    assert r.json() == {"a": "b", "c": "d"}


@pytest.mark.anyio
async def test_delete_config_var(client: AsyncClient) -> None:
    r = await client.delete("/config/a")
    assert r.status_code == 200


@pytest.mark.anyio
async def test_delete_config_var_not_exist(client: AsyncClient) -> None:
    r = await client.delete("/config/b")
    assert r.status_code == 404
