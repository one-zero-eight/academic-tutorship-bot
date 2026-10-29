from pathlib import Path

import pytest
from fluent.runtime import FluentLocalization, FluentResourceLoader

from src.bot.utils import is_allowed_email, parse_attendance, split_attendance_emails

LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"


def _make_i18n(locale: str) -> FluentLocalization:
    return FluentLocalization(
        [locale, "en"],
        ["handles.ftl"],
        FluentResourceLoader(str(LOCALES_DIR / "{locale}" / "LC_MESSAGES")),
    )


@pytest.mark.parametrize(
    "email",
    ["student@innopolis.university", "a.b+tag@innopolis.ru"],
)
def test_is_allowed_email_accepts_innopolis_domains(email: str):
    assert is_allowed_email(email)


@pytest.mark.parametrize(
    "email",
    [
        "student@gmail.com",
        "student@innopolis.com",
        "student@innopolis.university.evil.com",
        "student@innopolis.university ",
        "innopolis.ru",
    ],
)
def test_is_allowed_email_rejects_other_domains(email: str):
    assert not is_allowed_email(email)


def test_split_attendance_emails_keeps_valid_and_collects_invalid():
    valid, invalid = split_attendance_emails(
        ["a@innopolis.ru", "b@gmail.com", "a@innopolis.ru", "c@innopolis.university", "b@gmail.com"]
    )
    assert valid == ["a@innopolis.ru", "c@innopolis.university"]
    assert invalid == ["b@gmail.com"]


def test_split_attendance_emails_all_invalid():
    valid, invalid = split_attendance_emails(["x@mail.ru", "y@innopolis.com"])
    assert valid == []
    assert invalid == ["x@mail.ru", "y@innopolis.com"]


def test_parse_attendance_file_then_split():
    content = "a@innopolis.ru\nb@gmail.com\n"
    valid, invalid = split_attendance_emails(parse_attendance(content))
    assert valid == ["a@innopolis.ru"]
    assert invalid == ["b@gmail.com"]


@pytest.mark.parametrize("locale", ["en", "ru"])
def test_invalid_email_messages_have_expected_arguments(locale: str):
    l10n = _make_i18n(locale)
    assert l10n.format_value("Q_ATTENDANCE_INVALID_EMAIL")
    assert l10n.format_value("Q_ATTENDANCE_FILE_NO_EMAILS")
    assert l10n.format_value("Q_ATTENDANCE_FILE_INVALID_EMAILS_ALL")
    text = l10n.format_value("Q_ATTENDANCE_FILE_INVALID_EMAILS", {"count": 2})
    assert "2" in text
