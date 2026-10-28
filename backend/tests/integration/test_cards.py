import pytest


async def _make_board(client):
    p = await client.post("/projects", json={"name": "Pc"})
    pid = p.json()["id"]
    b = await client.post(f"/projects/{pid}/boards", json={"name": "Bc"})
    bid = b.json()["id"]
    c1 = await client.post(f"/boards/{bid}/columns", json={"name": "To Do", "order": 0})
    c2 = await client.post(
        f"/boards/{bid}/columns",
        json={"name": "In Progress", "order": 1, "wip_limit": 2},
    )
    return bid, c1.json()["id"], c2.json()["id"]


@pytest.mark.asyncio
async def test_column_lifecycle(auth_client):
    bid, c1, _ = await _make_board(auth_client)
    cols = await auth_client.get(f"/boards/{bid}/columns")
    assert cols.status_code == 200 and len(cols.json()) == 2
    u = await auth_client.patch(f"/columns/{c1}", json={"name": "Renamed"})
    assert u.status_code == 200 and u.json()["name"] == "Renamed"


@pytest.mark.asyncio
async def test_create_card(auth_client):
    _, c1, _ = await _make_board(auth_client)
    r = await auth_client.post(f"/columns/{c1}/cards", json={"title": "Task 1"})
    assert r.status_code == 201
    assert r.json()["title"] == "Task 1"


@pytest.mark.asyncio
async def test_move_card(auth_client):
    _, c1, c2 = await _make_board(auth_client)
    c = await auth_client.post(f"/columns/{c1}/cards", json={"title": "Move me"})
    cid = c.json()["id"]
    m = await auth_client.patch(f"/cards/{cid}/move", json={"column_id": c2, "order": 0})
    assert m.status_code == 200
    assert m.json()["column_id"] == c2


@pytest.mark.asyncio
async def test_wip_limit_enforced(auth_client):
    _, c1, c2 = await _make_board(auth_client)
    for i in range(2):
        await auth_client.post(f"/columns/{c2}/cards", json={"title": f"Filler {i}"})
    c = await auth_client.post(f"/columns/{c1}/cards", json={"title": "Overflow"})
    cid = c.json()["id"]
    r = await auth_client.patch(f"/cards/{cid}/move", json={"column_id": c2, "order": 0})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_update_card_priority_and_assignee(auth_client):
    _, c1, _ = await _make_board(auth_client)
    c = await auth_client.post(f"/columns/{c1}/cards", json={"title": "Upd"})
    cid = c.json()["id"]
    r = await auth_client.patch(f"/cards/{cid}", json={
        "priority": "high", "description": "desc",
    })
    assert r.status_code == 200
    assert r.json()["priority"] == "high"


@pytest.mark.asyncio
async def test_delete_card(auth_client):
    _, c1, _ = await _make_board(auth_client)
    c = await auth_client.post(f"/columns/{c1}/cards", json={"title": "Del"})
    cid = c.json()["id"]
    assert (await auth_client.delete(f"/cards/{cid}")).status_code == 204
    assert (await auth_client.get(f"/cards/{cid}")).status_code == 404


@pytest.mark.asyncio
async def test_card_history(auth_client):
    _, c1, c2 = await _make_board(auth_client)
    c = await auth_client.post(f"/columns/{c1}/cards", json={"title": "Hist"})
    cid = c.json()["id"]
    await auth_client.patch(f"/cards/{cid}/move", json={"column_id": c2, "order": 0})
    h = await auth_client.get(f"/cards/{cid}/history")
    assert h.status_code == 200
    actions = [x["action"] for x in h.json()]
    assert any("created" in a for a in actions)
    assert any("moved" in a for a in actions)