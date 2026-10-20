from datetime import date, timedelta

import pytest

from gdpr_erasure_kit.dates import (
    deadline,
    escalate_on,
    follow_up_on,
    localized,
    parse_date,
    reminder_on,
    schedule,
)


@pytest.mark.parametrize(
    "received,expected,extended",
    [
        ("2023-01-31", "2023-02-28", False),
        ("2024-01-31", "2024-02-29", False),
        ("2026-08-31", "2026-09-30", False),
        ("2026-11-30", "2026-12-30", False),
        ("2026-12-20", "2027-01-20", False),
        ("2026-09-10", "2026-10-12", False),
        ("2026-09-11", "2026-10-12", False),
        ("2026-10-20", "2026-11-20", False),
        ("2026-11-30", "2027-03-01", True),
        ("2023-11-30", "2024-02-29", True),
        ("2026-01-31", "2026-04-30", True),
        ("2026-10-20", "2027-01-20", True),
        ("2026-07-10", "2026-10-12", True),
        ("2026-01-31", "2026-03-02", False),
    ],
)
def test_deadline(received, expected, extended):
    assert deadline(date.fromisoformat(received), extended=extended) == date.fromisoformat(expected)


def test_offsets_do_not_shift_weekends():
    due = date(2026, 11, 20)
    assert reminder_on(due) == date(2026, 11, 15)
    assert follow_up_on(due) == date(2026, 11, 21)
    assert escalate_on(due) == date(2026, 12, 4)
    assert reminder_on(due) == due - timedelta(days=5)


def test_identity_resets_normal_and_extended_origin():
    sent, identity = date(2026, 10, 20), date(2026, 11, 5)
    assert schedule(sent, identity_sent_on=identity)["deadline"] == date(2026, 12, 7)
    assert schedule(sent, identity_sent_on=identity, extended=True)["deadline"] == date(2027, 2, 5)


@pytest.mark.parametrize("value", ["20260101", "2026-W01-1", "2026-1-01", "2026-02-30", "invalid"])
def test_parse_date_rejects_non_iso(value):
    with pytest.raises(ValueError):
        parse_date(value)


def test_localization():
    assert localized(date(2026, 11, 20), "en") == "20 November 2026"
    assert localized(date(2026, 11, 20), "fi") == "20.11.2026"
