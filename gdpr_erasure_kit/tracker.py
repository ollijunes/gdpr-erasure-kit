"""Tracker serialization and action selection without trusting stored deadlines."""

import csv
from datetime import date
from pathlib import Path
from typing import TextIO

from .dates import parse_date, schedule
from .io import InputError, escape_cell, read_csv, validate_service

COLUMNS = (
    "service",
    "contact",
    "request_type",
    "language",
    "status",
    "sent_on",
    "deadline",
    "reminder_on",
    "follow_up_on",
    "escalate_on",
    "identity_sent_on",
    "extended_deadline",
    "replied_on",
    "outcome",
    "notes",
)
STATUSES = {
    "draft",
    "sent",
    "acknowledged",
    "identity_requested",
    "extended",
    "completed",
    "refused",
    "escalated",
}
CLOSED = {"completed", "refused", "escalated"}


def draft_row(service: dict[str, str], sent_on: date | None) -> dict[str, str]:
    row = {key: service.get(key, "") for key in COLUMNS}
    for key in COLUMNS:
        if key.endswith("_on") or "deadline" in key:
            row[key] = ""
    row["status"] = "draft"
    if sent_on:
        row["status"] = "sent"
        row["sent_on"] = sent_on.isoformat()
        row.update({key: value.isoformat() for key, value in schedule(sent_on).items()})
    return row


def write_tracker(target: TextIO, rows: list[dict[str, str]]) -> None:
    writer = csv.DictWriter(target, fieldnames=COLUMNS)
    writer.writeheader()
    writer.writerows({key: escape_cell(row.get(key, "")) for key in COLUMNS} for row in rows)


def due_actions(path: Path, today: date) -> list[tuple[str, str, str, date]]:
    actions = []
    for number, row in read_csv(path, COLUMNS, COLUMNS):
        validate_service(row, path, number)
        status = row["status"]
        if status not in STATUSES:
            raise InputError(path, number, "Unknown tracker status.")
        try:
            sent = parse_date(row["sent_on"]) if row["sent_on"] else None
            identity_sent = parse_date(row["identity_sent_on"]) if row["identity_sent_on"] else None
            if row["replied_on"]:
                parse_date(row["replied_on"])
            if status in CLOSED:
                continue
            if status == "identity_requested" and not identity_sent:
                actions.append(
                    (row["service"], status, "waiting for your identity reply", sent or today)
                )
                continue
            if status == "draft" and not sent:
                actions.append((row["service"], status, "not sent yet", today))
                continue
            if not sent and not identity_sent:
                raise InputError(path, number, "Receipt date is required for this status.")
            dates = schedule(
                identity_sent or sent, identity_sent_on=identity_sent, extended=status == "extended"
            )
            for key, action in (
                ("escalate_on", "escalate to the supervisory authority"),
                ("follow_up_on", "follow up"),
                ("reminder_on", "reminder"),
            ):
                if today >= dates[key]:
                    actions.append((row["service"], status, action, dates[key]))
                    break
        except (ValueError, OverflowError) as exc:
            if isinstance(exc, InputError):
                raise
            raise InputError(path, number, "Invalid or out-of-range tracker date.") from exc
    return actions
