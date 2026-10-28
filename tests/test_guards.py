import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const

from src.bot.dialog_extension import StatusGuard, StatusGuardedDialog, require_status
from src.bot.exceptions import AuthorityException
from src.domain.models import UserStatus

USER = SimpleNamespace(id=42)


class GuardedStates(StatesGroup):
    first = State()


def _mock_roles(monkeypatch: pytest.MonkeyPatch, *, tutor: bool = False, admin: bool = False) -> None:
    monkeypatch.setattr("src.bot.filters.tutor_repo.exists", AsyncMock(return_value=tutor))
    monkeypatch.setattr("src.bot.filters.student_repo.is_admin", AsyncMock(return_value=admin))


def _dialog(*statuses: UserStatus) -> StatusGuardedDialog:
    window = Window(Const("test"), state=GuardedStates.first)
    return StatusGuardedDialog(window, guard=StatusGuard(statuses))


def _filters(dialog: StatusGuardedDialog) -> list[str]:
    assert dialog.callback_query._handler.filters
    return [type(filter_.callback).__name__ for filter_ in dialog.callback_query._handler.filters]


def _manager(user=USER) -> SimpleNamespace:
    return SimpleNamespace(
        middleware_data={"event_from_user": user},
        switch_to=AsyncMock(),
    )


def test_guard_is_installed_after_intent_filter():
    dialog = _dialog(UserStatus.admin)

    assert _filters(dialog) == ["IntentFilter", "StatusGuard"]
    assert _filters(dialog)[0] == "IntentFilter"


@pytest.mark.asyncio
async def test_dialog_rejects_denied_status(monkeypatch):
    _mock_roles(monkeypatch)
    dialog = _dialog(UserStatus.admin)

    allowed, _ = await dialog.callback_query.check_root_filters(
        SimpleNamespace(),  # type: ignore
        event_from_user=USER,
        aiogd_context=SimpleNamespace(state=GuardedStates.first),
    )

    assert allowed is False


@pytest.mark.asyncio
async def test_dialog_allows_required_status(monkeypatch):
    _mock_roles(monkeypatch, admin=True)
    dialog = _dialog(UserStatus.admin)

    allowed, _ = await dialog.callback_query.check_root_filters(
        SimpleNamespace(),  # type: ignore
        event_from_user=USER,
        aiogd_context=SimpleNamespace(state=GuardedStates.first),
    )

    assert allowed is True


@pytest.mark.asyncio
async def test_dialog_allows_admin_tutor_for_tutor_branch(monkeypatch):
    _mock_roles(monkeypatch, tutor=True, admin=True)
    dialog = _dialog(UserStatus.tutor)

    allowed, _ = await dialog.callback_query.check_root_filters(
        SimpleNamespace(),  # type: ignore
        event_from_user=USER,
        aiogd_context=SimpleNamespace(state=GuardedStates.first),
    )

    assert allowed is True


@pytest.mark.asyncio
async def test_process_start_raises_for_denied_status(monkeypatch):
    _mock_roles(monkeypatch)
    dialog = _dialog(UserStatus.admin)
    manager = _manager()

    with pytest.raises(AuthorityException):
        await dialog.process_start(manager, {}, GuardedStates.first)  # type: ignore

    manager.switch_to.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_start_opens_dialog_for_allowed_status(monkeypatch):
    _mock_roles(monkeypatch, admin=True)
    dialog = _dialog(UserStatus.admin)
    manager = _manager()

    await dialog.process_start(manager, {}, GuardedStates.first)  # type: ignore

    manager.switch_to.assert_awaited_once_with(GuardedStates.first)


@pytest.mark.asyncio
async def test_require_status_allows_allowed_handler(monkeypatch):
    _mock_roles(monkeypatch, admin=True)

    @require_status(UserStatus.admin)
    async def handler(event, widget, manager, item_id):
        return item_id

    assert await handler(SimpleNamespace(from_user=USER), None, None, "7") == "7"


@pytest.mark.asyncio
async def test_require_status_raises_for_denied_handler(monkeypatch):
    _mock_roles(monkeypatch, tutor=True)

    @require_status(UserStatus.admin)
    async def handler(event, widget, manager):
        raise AssertionError("handler must not be called")

    with pytest.raises(AuthorityException):
        await handler(SimpleNamespace(from_user=USER), None, None)


@pytest.mark.asyncio
async def test_require_status_respects_forbidden(monkeypatch):
    _mock_roles(monkeypatch, tutor=True, admin=True)

    @require_status(UserStatus.tutor, forbidden=(UserStatus.admin,))
    async def handler(event, widget, manager):
        raise AssertionError("handler must not be called")

    with pytest.raises(AuthorityException):
        await handler(SimpleNamespace(from_user=USER), None, None)


@pytest.mark.asyncio
async def test_require_status_raises_without_user():
    @require_status(UserStatus.admin)
    async def handler(event, widget, manager):
        raise AssertionError("handler must not be called")

    with pytest.raises(AuthorityException):
        await handler(SimpleNamespace(), None, None)


async def _is_dialog_allowed(monkeypatch, dialog, *, tutor: bool, admin: bool) -> bool:
    _mock_roles(monkeypatch, tutor=tutor, admin=admin)
    allowed, _ = await dialog.callback_query.check_root_filters(
        SimpleNamespace(),
        event_from_user=USER,
        aiogd_context=SimpleNamespace(state=dialog.states()[0]),
    )
    return allowed


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module_name", "student_allowed", "tutor_allowed", "admin_allowed"),
    [
        ("src.bot.dialogs.tutors", False, False, True),
        ("src.bot.dialogs.disciplines_control", False, False, True),
        ("src.bot.dialogs.meetings", False, True, True),
        ("src.bot.dialogs.change_meeting", False, True, True),
        ("src.bot.dialogs.attendance", False, True, True),
        ("src.bot.dialogs.tutors_profile", True, True, True),
        ("src.bot.dialogs.student_meetings", True, True, True),
        ("src.bot.dialogs.root", True, True, True),
    ],
)
async def test_project_dialog_guards(
    monkeypatch, module_name: str, student_allowed: bool, tutor_allowed: bool, admin_allowed: bool
):
    dialog = importlib.import_module(module_name).dialog

    assert await _is_dialog_allowed(monkeypatch, dialog, tutor=False, admin=False) is student_allowed
    assert await _is_dialog_allowed(monkeypatch, dialog, tutor=True, admin=False) is tutor_allowed
    assert await _is_dialog_allowed(monkeypatch, dialog, tutor=False, admin=True) is admin_allowed
