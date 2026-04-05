import pytest_asyncio

from src.db.repositories import (
    AdminRepository,
    DisciplineRepository,
    MeetingRepository,
    SQLDatabase,
    StudentRepository,
    TutorRepository,
)
from src.db.schema import metadata


@pytest_asyncio.fixture
async def db():
    db = SQLDatabase("sqlite+aiosqlite:///:memory:", dumb=True)
    async with db.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield db
    await db.dispose()


@pytest_asyncio.fixture
async def student_repo(db):
    return StudentRepository(db)


@pytest_asyncio.fixture
async def tutor_repo(db):
    return TutorRepository(db)


@pytest_asyncio.fixture
async def admin_repo(db):
    return AdminRepository(db)


@pytest_asyncio.fixture
async def meeting_repo(db):
    return MeetingRepository(db)


@pytest_asyncio.fixture
async def discipline_repo(db):
    return DisciplineRepository(db)
