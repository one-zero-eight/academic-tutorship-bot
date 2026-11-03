from datetime import date, datetime

from src.bot.i18n import format_date, format_datetime, normalize_l10n_kwargs, normalize_l10n_value


def test_format_datetime_uses_required_format():
    assert format_datetime(datetime(2026, 11, 3, 14, 53, 42)) == "03.11.2026 14:53"


def test_format_datetime_default_for_none():
    assert format_datetime(None) == "-"
    assert format_datetime(None, default="N/A") == "N/A"


def test_format_date_uses_required_format():
    assert format_date(date(2026, 11, 3)) == "03.11.2026"


def test_normalize_l10n_value_formats_datetime_and_date():
    assert normalize_l10n_value(datetime(2026, 11, 3, 14, 53)) == "03.11.2026 14:53"
    assert normalize_l10n_value(date(2026, 11, 3)) == "03.11.2026"


def test_normalize_l10n_kwargs_formats_nested_values():
    data = {
        "datetime": datetime(2026, 11, 3, 14, 53),
        "items": [{"date": date(2026, 11, 3)}],
    }
    assert normalize_l10n_kwargs(data) == {
        "datetime": "03.11.2026 14:53",
        "items": [{"date": "03.11.2026"}],
    }
