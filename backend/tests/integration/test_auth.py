import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    r = await client.post("/auth/register", json={
        "email": "a1@example.com", "password": "password123", "role": "admin",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "a1@example.com"
    assert data["role"] == "admin"
    assert "password" not in data and "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_409(client):
    payload = {"email": "a2@example.com", "password": "password123", "role": "developer"}
    assert (await client.post("/auth/register", json=payload)).status_code == 201
    assert (await client.post("/auth/register", json=payload)).status_code == 409


@pytest.mark.asyncio
async def test_login_ok(client):
    await client.post("/auth/register", json={
        "email": "a3@example.com", "password": "password123", "role": "developer",
    })
    r = await client.post("/auth/login", json={
        "email": "a3@example.com", "password": "password123",
    })
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_401(client):
    await client.post("/auth/register", json={
        "email": "a4@example.com", "password": "password123", "role": "developer",
    })
    r = await client.post("/auth/login", json={
        "email": "a4@example.com", "password": "wrong",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_401(client):
    assert (await client.get("/auth/me")).status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(auth_client):
    r = await auth_client.get("/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "itest@example.com"


@pytest.mark.asyncio
async def test_refresh_token(auth_client):
    login = await auth_client.post("/auth/login", json={
        "email": "itest@example.com", "password": "password123",
    })
    refresh = login.json()["refresh_token"]
    r = await auth_client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_users_list(auth_client):
    r = await auth_client.get("/auth/users")
    assert r.status_code == 200
    assert isinstance(r.json(), list)