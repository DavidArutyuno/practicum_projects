import inspect
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from mixer.backend.sqlalchemy import Mixer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from app.main import app  # noqa
except (NameError, ImportError) as error:
    raise AssertionError(
        'При импорте объекта приложения `app` из модуля `app.main` '
        f'возникло исключение:\n{type(error).__name__}: {error}.'
    )

try:
    from app.core.db import Base, get_async_session  # noqa
except (NameError, ImportError) as error:
    raise AssertionError(
        'При импорте объектов `Base, get_async_session` '
        'из модуля `app.core.db` возникло исключение:\n'
        f'{type(error).__name__}: {error}.'
    )


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

pytest_plugins = [
    'fixtures.data',
]

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite://"

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AsyncTestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_db():
    async with AsyncTestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_db


@pytest_asyncio.fixture
async def session():
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture
def charity_project_model():
    models = Base.registry._class_registry.values()
    charity_project_model = [
        model for model in models if (
            inspect.isclass(model) and
            issubclass(model, Base) and
            model.__name__ == 'CharityProject'
        )
    ]
    assert charity_project_model, (
        'Убедитесь, что создали модель `CharityProject`.'
    )
    return charity_project_model[0]


@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def mixer():
    async with AsyncTestingSessionLocal() as session:
        mixer = Mixer(session=session)
        yield mixer
