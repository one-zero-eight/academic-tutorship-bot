from collections.abc import Callable
from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader

from src.db.repositories.discipline import BlockingMeeting, DisciplineInUseError
from src.domain.models import Discipline, MeetingStatus
from src.utils.disciplines import build_disciplines_added_message, build_disciplines_deleted_message

LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"


def _make_i18n(locale: str = "en") -> Callable[[str, dict], str]:
    l10n = FluentLocalization(
        [locale, "en"],
        ["dialog.ftl", "handles.ftl"],
        FluentResourceLoader(str(LOCALES_DIR / "{locale}" / "LC_MESSAGES")),
    )

    def translate_func(key: str, data: dict) -> str:
        return l10n.format_value(key, data)

    return translate_func


def _discipline(**overrides) -> Discipline:
    data = {"id": 3, "name": "Mathematical Analysis", "year": 1, "semester": 1, "language": "EN"}
    return Discipline(**(data | overrides))


def test_add_message_when_nothing_added():
    assert build_disciplines_added_message([], _make_i18n()) == "No disciplines were added."


def test_add_message_lists_added_disciplines():
    assert (
        build_disciplines_added_message([_discipline()], _make_i18n())
        == "Disciplines Added:\n3. [EN 1y 1s] Mathematical Analysis"
    )


def test_delete_message_when_deleted_and_errored():
    error = DisciplineInUseError(
        _discipline(id=7, name="Physics"),
        [BlockingMeeting(id=2, title="Physics Recap", status=MeetingStatus.ANNOUNCED)],
    )

    message = build_disciplines_deleted_message([_discipline()], [error], _make_i18n())

    assert message == (
        "Disciplines Deleted:\n"
        "3. [EN 1y 1s] Mathematical Analysis"
        "\n\n"
        "Deletion Errors:\n"
        "⚠️  7. Physics is used in meetings:\n"
        "- 2. Physics Recap, ANNOUNCED (change/delete)"
    )


def test_delete_message_when_nothing_deleted_but_errored():
    error = DisciplineInUseError(
        _discipline(id=7, name="Physics"),
        [BlockingMeeting(id=2, title="Physics Recap", status=MeetingStatus.APPROVING)],
    )

    message = build_disciplines_deleted_message([], [error], _make_i18n())

    assert message == (
        "No disciplines were deleted."
        "\n\n"
        "Deletion Errors:\n"
        "⚠️  7. Physics is used in meetings:\n"
        "- 2. Physics Recap, APPROVING (disapprove + change/delete)"
    )


def test_delete_message_when_nothing_deleted_and_no_errors():
    assert (
        build_disciplines_deleted_message([], [], _make_i18n())
        == "No disciplines were deleted: no matching disciplines found."
    )


def test_delete_message_when_only_deleted():
    assert (
        build_disciplines_deleted_message([_discipline()], [], _make_i18n())
        == "Disciplines Deleted:\n3. [EN 1y 1s] Mathematical Analysis"
    )


def test_messages_are_localised():
    i18n = _make_i18n("ru")

    assert build_disciplines_added_message([], i18n) == "Ни одна дисциплина не добавлена."
    assert build_disciplines_deleted_message([], [], i18n) == "Ни одна дисциплина не удалена: совпадений не найдено."


def test_delete_message_escapes_names():
    error = DisciplineInUseError(
        _discipline(id=7, name="Math <I>"),
        [BlockingMeeting(id=1, title="Approval <one>", status=MeetingStatus.APPROVING)],
    )

    message = build_disciplines_deleted_message([], [error], _make_i18n())

    assert "⚠️  7. Math &lt;I&gt; is used in meetings:" in message
    assert "- 1. Approval &lt;one&gt;, APPROVING (disapprove + change/delete)" in message
