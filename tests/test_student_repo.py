import pytest

from src.config import settings as app_settings
from src.db.repositories import StudentRepository
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create(student_repo: StudentRepository, monkeypatch):
    monkeypatch.setattr(app_settings, "admins", [])
    data = {
        "telegram_id": 1,
        "first_name": "test",
        "last_name": "user",
        "username": "testusername",
        "email_": "test.user@innopolis.university",
    }
    student = await student_repo.create(**data)
    student_dump = student.model_dump()
    student_dump.update({"email_": student.email})
    assert data.items() <= student_dump.items()
    assert student.is_admin is False
    assert student.settings.receive_notifications is True
    assert await student_repo.exists(telegram_id=data["telegram_id"])


@pytest.mark.asyncio
async def test_create_marks_admin_if_in_config(student_repo: StudentRepository, monkeypatch):
    monkeypatch.setattr(app_settings, "admins", [777])
    data = {
        "telegram_id": 777,
        "first_name": "admin",
        "last_name": "user",
        "username": "adminuser",
        "email_": "admin.user@innopolis.university",
    }

    student = await student_repo.create(**data)

    assert student.telegram_id == data["telegram_id"]
    assert student.is_admin is True
