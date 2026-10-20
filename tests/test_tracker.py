import csv
from datetime import date

import pytest

from gdpr_erasure_kit.io import InputError
from gdpr_erasure_kit.tracker import COLUMNS, draft_row, due_actions, write_tracker


@pytest.mark.parametrize(
    "status",
    [
        "draft",
        "sent",
        "acknowledged",
        "identity_requested",
        "extended",
        "completed",
        "refused",
        "escalated",
    ],
)
def test_each_status(tracker_file, status):
    path = tracker_file({"status": status})
    actions = due_actions(path, date(2026, 11, 21))
    if status in {"extended", "completed", "refused", "escalated"}:
        assert actions == []
    elif status == "identity_requested":
        assert actions[0][2:] == ("waiting for your identity reply", date(2026, 10, 20))
    else:
        assert actions[0][2:] == ("follow up", date(2026, 11, 21))


@pytest.mark.parametrize(
    "today,action,when",
    [
        ("2026-11-14", None, None),
        ("2026-11-15", "reminder", "2026-11-15"),
        ("2026-11-20", "reminder", "2026-11-15"),
        ("2026-11-21", "follow up", "2026-11-21"),
        ("2026-12-03", "follow up", "2026-11-21"),
        ("2026-12-04", "escalate to the supervisory authority", "2026-12-04"),
    ],
)
def test_action_boundaries_and_priority(tracker_file, today, action, when):
    path = tracker_file({"deadline": "invalid stored date", "reminder_on": "1999-01-01"})
    actions = due_actions(path, date.fromisoformat(today))
    if action:
        assert len(actions) == 1
        assert actions[0][2:] == (action, date.fromisoformat(when))
    else:
        assert not actions


def test_unsent_draft_and_waiting_identity_without_date(tracker_file):
    path = tracker_file(
        {"status": "draft", "sent_on": ""}, {"status": "identity_requested", "sent_on": ""}
    )
    actions = due_actions(path, date(2026, 10, 20))
    assert [row[2] for row in actions] == ["not sent yet", "waiting for your identity reply"]


def test_identity_reply_and_extension(tracker_file):
    path = tracker_file({"status": "identity_requested", "identity_sent_on": "2026-11-05"})
    assert due_actions(path, date(2026, 11, 21)) == []
    assert due_actions(path, date(2026, 12, 8))[0][2:] == ("follow up", date(2026, 12, 8))
    path = tracker_file({"status": "extended", "identity_sent_on": "2026-11-05"})
    assert due_actions(path, date(2027, 2, 6))[0][2:] == ("follow up", date(2027, 2, 6))


def test_draft_without_sent_date_stays_unsent(tracker_file):
    path = tracker_file({"status": "draft", "sent_on": "", "identity_sent_on": "2026-10-20"})
    assert due_actions(path, date(2026, 12, 8))[0][2] == "not sent yet"


@pytest.mark.parametrize(
    "row",
    [
        {"status": "PRIVATE_CELL"},
        {"sent_on": "PRIVATE_CELL"},
        {"sent_on": ""},
        {"identity_sent_on": "PRIVATE_CELL"},
        {"replied_on": "PRIVATE_CELL"},
        {"sent_on": "9999-12-01"},
    ],
)
def test_tracker_errors_are_redacted(tracker_file, row):
    path = tracker_file(row)
    with pytest.raises(InputError) as failure:
        due_actions(path, date(2026, 11, 21))
    assert str(path) in str(failure.value) and "row 2:" in str(failure.value)
    assert "PRIVATE_CELL" not in str(failure.value)


def test_draft_rows_and_csv_writer(service, tmp_path):
    service.update(
        {
            column: "2026-01-01"
            for column in COLUMNS
            if column.endswith("_on") or "deadline" in column
        }
    )
    service["status"] = "completed"
    row = draft_row(service, None)
    assert row["status"] == "draft"
    assert all(
        not row[column] for column in COLUMNS if column.endswith("_on") or "deadline" in column
    )
    dated = draft_row(service, date(2026, 10, 20))
    assert dated["status"] == "sent"
    assert dated["deadline"] == "2026-11-20"
    assert dated["sent_on"] == "2026-10-20"
    assert dated["extended_deadline"] == ""
    dated.update(service="=Example", notes="+private fixture note")
    path = tmp_path / "output.csv"
    with path.open("w", encoding="utf-8", newline="") as output:
        write_tracker(output, [dated])
    assert not path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        assert tuple(reader.fieldnames) == COLUMNS
        result = next(reader)
    assert result["service"] == "'=Example"
    assert result["notes"] == "'+private fixture note"
    assert due_actions(path, date(2026, 11, 21))[0][0] == "=Example"
