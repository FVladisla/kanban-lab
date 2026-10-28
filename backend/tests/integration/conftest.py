import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from sqlalchemy.pool import NullPool
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401 — регистрирует все модели в metadata


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as pg:
        yield pg


@pytest_asyncio.fixture(scope="session")
async def engine(postgres_container):
    url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2", "postgresql+asyncpg"
    )

    eng = create_async_engine(url, echo=False, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def client(engine):
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with Session() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    """Клиент с уже авторизованным админом."""
    email = "itest@example.com"
    password = "password123"
    await client.post("/auth/register", json={
        "email": email, "password": password, "role": "admin",
    })
    login = await client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def dev_client(client):
    """Клиент с авторизованным разработчиком."""
    email = "dev@example.com"
    password = "password123"
    await client.post("/auth/register", json={
        "email": email, "password": password, "role": "developer",
    })
    login = await client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client