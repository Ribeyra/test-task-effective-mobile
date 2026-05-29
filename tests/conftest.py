import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.api.deps import get_db
from app.core.database import Base
from app.main import app as _app
from app.models.models import Resource, Role, User, UserRole

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/auth_system_test"  # noqa e501


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as s:
        yield s


@pytest_asyncio.fixture
async def seed_data(session: AsyncSession):
    admin_role = Role(
        id=uuid.uuid4(), name="admin", description="Admin", is_system=True
    )
    viewer_role = Role(
        id=uuid.uuid4(), name="viewer", description="Viewer", is_system=False
    )
    session.add(admin_role)
    session.add(viewer_role)
    await session.flush()

    orders = Resource(id=uuid.uuid4(), name="orders", description="Orders")
    products = Resource(
        id=uuid.uuid4(), name="products", description="Products"
    )
    session.add(orders)
    session.add(products)
    await session.flush()

    admin_user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        password_hash=pwd.hash("admin123"),
        first_name="Admin",
        last_name="Test",
        is_superuser=True,
        is_active=True,
    )
    session.add(admin_user)
    await session.flush()
    session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
    await session.flush()

    regular_user = User(
        id=uuid.uuid4(),
        email="user@test.com",
        password_hash=pwd.hash("user123"),
        first_name="Regular",
        last_name="User",
        is_superuser=False,
        is_active=True,
    )
    session.add(regular_user)
    await session.flush()
    session.add(UserRole(user_id=regular_user.id, role_id=viewer_role.id))
    await session.flush()

    return {
        "admin_role": admin_role,
        "viewer_role": viewer_role,
        "orders": orders,
        "products": products,
        "admin_user": admin_user,
        "regular_user": regular_user,
    }


@pytest_asyncio.fixture
async def app(engine, session) -> AsyncGenerator:
    app = _app
    async def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, seed_data: dict) -> dict:
    resp = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
