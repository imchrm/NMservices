"""Pytest configuration and fixtures for tests."""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient

from nms.main import app
from nms.database import get_db, Base
from nms.config import get_settings

settings = get_settings()

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# Create test session factory
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    Each test gets a fresh database with tables created.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide session
    async with test_async_session_maker() as session:
        yield session

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession):
    """
    Create a test client with overridden database dependency.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_api_key() -> str:
    """Return valid API key for tests."""
    return settings.api_secret_key


@pytest.fixture
def wrong_api_key() -> str:
    """Return invalid API key for tests."""
    return "wrong_password"


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> int:
    """
    Create a test user in the database.

    Returns:
        User ID of created test user
    """
    from nms.models.db_models import User

    user = User(phone_number="+998901234567")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user.id


@pytest_asyncio.fixture
async def test_user_with_telegram(db_session: AsyncSession) -> dict:
    """
    Create a test user with telegram_id in the database.

    Returns:
        Dict with user_id and telegram_id
    """
    from nms.models.db_models import User

    user = User(phone_number="+998909876543", telegram_id=192496135)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {"user_id": user.id, "telegram_id": user.telegram_id}


@pytest_asyncio.fixture
async def test_service(db_session: AsyncSession) -> int:
    """
    Create a test service in the database.

    Returns:
        Service ID of created test service
    """
    from nms.models.db_models import Service
    from decimal import Decimal

    service = Service(
        name="Test Massage",
        description="Test massage service",
        base_price=Decimal("150000.00"),
        duration_minutes=60,
        is_active=True,
    )
    db_session.add(service)
    await db_session.commit()
    await db_session.refresh(service)

    return service.id
