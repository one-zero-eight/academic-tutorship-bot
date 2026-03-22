import pytest

from src.db.repositories import AdminRepository, StudentRepository
from tests.fixtures import *


@pytest.mark.asyncio
async def test_sync_with_config_skips_non_existing_students(
    student_repo: StudentRepository,
    admin_repo: AdminRepository,
):
    await student_repo.create(
        telegram_id=100,
        first_name="Admin",
        last_name="One",
        username="admin_one",
        email_="admin.one@innopolis.university",
    )
    await student_repo.create(
        telegram_id=200,
        first_name="Admin",
        last_name="Two",
        username="admin_two",
        email_="admin.two@innopolis.university",
    )

    added, removed = await admin_repo.sync_with_config([100, 999])

    assert set(added) == {100}
    assert removed == []
    assert set(await admin_repo.get_telegram_ids()) == {100}

    added, removed = await admin_repo.sync_with_config([200, 999])

    assert set(added) == {200}
    assert set(removed) == {100}
    assert set(await admin_repo.get_telegram_ids()) == {200}
