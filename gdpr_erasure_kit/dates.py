"""Calendar periods under Article 12(3) and EDPB 01/2022, paragraphs 159–162."""

import calendar
import re
from datetime import date, timedelta


class DateRangeError(ValueError):
    pass


def parse_date(value: str) -> date:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Expected an ISO date.")
    return date.fromisoformat(value)


def deadline(received: date, *, extended: bool = False) -> date:
    """Add one (or three) calendar months, clamp the day, then shift weekends.

    The receipt day is the origin. Public holidays are not considered.
    """
    month_index = received.year * 12 + received.month - 1 + (3 if extended else 1)
    year, month_index = divmod(month_index, 12)
    if year > date.max.year:
        raise DateRangeError("Date out of range.")
    month = month_index + 1
    day = min(received.day, calendar.monthrange(year, month)[1])
    result = date(year, month, day)
    if result.weekday() >= 5:
        result += timedelta(days=7 - result.weekday())
    return result


def reminder_on(due: date) -> date:
    return due - timedelta(days=5)


def follow_up_on(due: date) -> date:
    return due + timedelta(days=1)


def escalate_on(due: date) -> date:
    return due + timedelta(days=14)


def schedule(
    sent_on: date, *, identity_sent_on: date | None = None, extended: bool = False
) -> dict[str, date]:
    """Restart at identity_sent_on after an identity-information suspension.

    EDPB paragraph 159 suspends the clock while identity information is awaited.
    The tracker models resumption by using identity_sent_on as the new origin.
    """
    due = deadline(identity_sent_on or sent_on, extended=extended)
    try:
        return {
            "deadline": due,
            "reminder_on": reminder_on(due),
            "follow_up_on": follow_up_on(due),
            "escalate_on": escalate_on(due),
        }
    except OverflowError as exc:
        raise DateRangeError("Date out of range.") from exc


def localized(value: date, language: str) -> str:
    if language == "fi":
        return f"{value.day}.{value.month}.{value.year}"
    months = (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
    return f"{value.day} {months[value.month - 1]} {value.year}"
