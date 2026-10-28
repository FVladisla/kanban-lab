import pytest


@pytest.mark.asyncio
async def test_create_project_as_admin(auth_client):
    r = await auth_client.post("/projects", json={"name": "P1", "description": "test"})
    assert r.status_code == 201
    assert r.json()["name"] == "P1"


@pytest.mark.asyncio
async def test_create_project_as_developer_403(dev_client):
    r = await dev_client.post("/projects", json={"name": "P", "description": "x"})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_list_projects(auth_client):
    await auth_client.post("/projects", json={"name": "P-list"})
    r = await auth_client.get("/projects")
    assert r.status_code == 200
    assert any(p["name"] == "P-list" for p in r.json())


@pytest.mark.asyncio
async def test_get_project_404(auth_client):
    assert (await auth_client.get("/projects/99999")).status_code == 404


@pytest.mark.asyncio
async def test_update_and_delete_project(auth_client):
    c = await auth_client.post("/projects", json={"name": "P-upd"})
    pid = c.json()["id"]
    u = await auth_client.patch(f"/projects/{pid}", json={"name": "P-upd2"})
    assert u.status_code == 200 and u.json()["name"] == "P-upd2"
    d = await auth_client.delete(f"/projects/{pid}")
    assert d.status_code == 204


@pytest.mark.asyncio
async def test_board_lifecycle(auth_client):
    p = await auth_client.post("/projects", json={"name": "P-b"})
    pid = p.json()["id"]
    b = await auth_client.post(f"/projects/{pid}/boards", json={"name": "B1"})
    assert b.status_code == 201
    bid = b.json()["id"]
    lst = await auth_client.get(f"/projects/{pid}/boards")
    assert lst.status_code == 200 and len(lst.json()) >= 1
    det = await auth_client.get(f"/boards/{bid}/details")
    assert det.status_code == 200
    assert det.json()["project_id"] == pid
    d = await auth_client.delete(f"/boards/{bid}")
    assert d.status_code == 204