import pytest


async def _card(client):
    p = await client.post("/projects", json={"name": "Px"})
    b = await client.post(f"/projects/{p.json()['id']}/boards", json={"name": "Bx"})
    c = await client.post(f"/boards/{b.json()['id']}/columns", json={"name": "C", "order": 0})
    card = await client.post(f"/columns/{c.json()['id']}/cards", json={"title": "X"})
    return card.json()["id"]


@pytest.mark.asyncio
async def test_search_by_text(auth_client):
    cid = await _card(auth_client)
    r = await auth_client.get("/cards", params={"search": "X"})
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json())


@pytest.mark.asyncio
async def test_comments_lifecycle(auth_client):
    cid = await _card(auth_client)
    r = await auth_client.post(f"/cards/{cid}/comments", json={"text": "hello"})
    assert r.status_code == 201
    lst = await auth_client.get(f"/cards/{cid}/comments")
    assert lst.status_code == 200 and len(lst.json()) == 1


@pytest.mark.asyncio
async def test_labels_attach_detach(auth_client):
    cid = await _card(auth_client)
    l = await auth_client.post("/labels", json={"name": "bug", "color": "#ff0000"})
    assert l.status_code == 201
    lid = l.json()["id"]
    a = await auth_client.post(f"/cards/{cid}/labels/{lid}")
    assert a.status_code == 204
    d = await auth_client.delete(f"/cards/{cid}/labels/{lid}")
    assert d.status_code == 204


@pytest.mark.asyncio
async def test_attachments_lifecycle(auth_client):
    cid = await _card(auth_client)
    r = await auth_client.post(f"/cards/{cid}/attachments", json={
        "filename": "f.txt", "url": "http://x/f.txt",
    })
    assert r.status_code == 201
    lst = await auth_client.get(f"/cards/{cid}/attachments")
    assert lst.status_code == 200 and len(lst.json()) == 1