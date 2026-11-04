from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.dialogs.root import handles
from src.domain.models import Discipline, Settings, Student

USER = SimpleNamespace(id=42)


def _manager(state: FSMContext) -> SimpleNamespace:
    return SimpleNamespace(
        middleware_data={
            "state": state,
            "event_chat": SimpleNamespace(id=42),
        },
        switch_to=AsyncMock(),
    )


@pytest.fixture
def state() -> FSMContext:
    return FSMContext(storage=MemoryStorage(), key=StorageKey(bot_id=1, chat_id=1, user_id=1))


@pytest.fixture
def student() -> Student:
    return Student(id=1, telegram_id=42, email="student@example.com", settings=Settings())


@pytest.mark.asyncio
async def test_open_disciplines_loads_from_db_when_state_is_empty(monkeypatch, state: FSMContext, student: Student):
    disciplines = [
        Discipline(id=1, name="Math", year=1, semester=1, language="EN"),
        Discipline(id=2, name="Physics", year=1, semester=1, language="EN"),
    ]
    await state.update_data({"self_student": student.model_dump()})
    monkeypatch.setattr(handles.student_repo, "get_relevant_disciplines", AsyncMock(return_value=disciplines))
    manager = _manager(state)

    await handles.on_open_disciplines(SimpleNamespace(from_user=USER), None, manager)

    assert await state.get_value("selected_disciplines") == [disc.model_dump() for disc in disciplines]


def test_settings_window_wires_disciplines_loader():
    from src.bot.dialogs.root import windows

    widget = windows.settings_ww.keyboard.find("open_disciplines")

    assert widget.on_click is not None
