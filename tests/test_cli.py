import csv
import os
import runpy
import socket
import subprocess
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from gdpr_erasure_kit.cli import main
from gdpr_erasure_kit.tracker import COLUMNS

ROOT = Path(__file__).resolve().parents[1]


def draft_args(tmp_path):
    return [
        "draft",
        "--services",
        str(ROOT / "examples/services.example.csv"),
        "--identity",
        str(ROOT / "examples/identity.example.toml"),
        "--out",
        str(tmp_path / "output"),
    ]


def test_example_end_to_end(tmp_path, capsys):
    assert main(draft_args(tmp_path) + ["--date", "2026-10-20", "--mark-sent"]) == 0
    output = tmp_path / "output"
    assert len(list(output.glob("*.txt"))) == 5
    assert (output / "03-blue-acorn-erasure-fi.txt").exists()
    assert (output / "04-copper-meadow-access-en.txt").exists()
    with (output / "tracker.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 5
    assert all(row["sent_on"] == "2026-10-20" and row["deadline"] == "2026-11-20" for row in rows)
    captured = capsys.readouterr()
    assert "5 drafts and 1 tracker" in captured.out
    assert "Rows marked sent." in captured.out
    assert "Alex Example" not in captured.out and "alex@example.com" not in captured.out
    assert not captured.err
    assert main(["due", "--tracker", str(output / "tracker.csv"), "--today", "2026-11-21"]) == 0
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 5 and "follow up" in captured.out
    assert "Example account" not in captured.out
    if os.name != "nt":
        assert all(path.stat().st_mode & 0o777 == 0o600 for path in output.iterdir())


@pytest.mark.parametrize("explicit_date", [False, True])
@pytest.mark.parametrize("mark_sent", [False, True])
def test_draft_letter_date_and_tracker_status(tmp_path, capsys, explicit_date, mark_sent):
    args = draft_args(tmp_path) + ["--lang", "fi", "--type", "access"]
    if explicit_date:
        args += ["--date", "2026-10-20"]
    if mark_sent:
        args += ["--mark-sent"]
    with patch("gdpr_erasure_kit.cli.date") as clock:
        clock.today.return_value = date(2026, 10, 21)
        assert main(args) == 0
    day = "20" if explicit_date else "21"
    output = tmp_path / "output"
    letter = (output / "01-cloud-pebble-access-fi.txt").read_text(encoding="utf-8")
    assert f"{day}.10.2026" in letter
    assert ("20.11.2026" if explicit_date else "23.11.2026") in letter
    with (output / "tracker.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    expected_dates = {key: "" for key in COLUMNS if key.endswith("_on") or "deadline" in key}
    if mark_sent:
        expected_dates.update(
            sent_on=f"2026-10-{day}",
            deadline="2026-11-20" if explicit_date else "2026-11-23",
            reminder_on="2026-11-15" if explicit_date else "2026-11-18",
            follow_up_on="2026-11-21" if explicit_date else "2026-11-24",
            escalate_on="2026-12-04" if explicit_date else "2026-12-07",
        )
    assert len(rows) == 5
    for row in rows:
        assert row["status"] == ("sent" if mark_sent else "draft")
        assert {key: row[key] for key in expected_dates} == expected_dates
    summary = capsys.readouterr()
    assert (
        "Rows marked sent." if mark_sent else "Rows left as draft (not marked sent)."
    ) in summary.out
    assert summary.err == ""
    if not mark_sent:
        assert main(["due", "--tracker", str(output / "tracker.csv")]) == 0
        assert capsys.readouterr().out.count("not sent yet") == 5


@pytest.mark.parametrize("explicit_today", [False, True])
@pytest.mark.parametrize("rows", [(), ({},), ({"status": "completed"},)])
def test_due_nothing_due(tracker_file, capsys, explicit_today, rows):
    path = tracker_file(*rows)
    args = ["due", "--tracker", str(path)]
    if explicit_today:
        args += ["--today", "2026-10-22"]
    with patch("gdpr_erasure_kit.cli.date") as clock:
        clock.today.return_value = date(2026, 10, 21)
        assert main(args) == 0
    result = capsys.readouterr()
    day = "22" if explicit_today else "21"
    assert result.out == f"Nothing due on 2026-10-{day}.\n"
    assert result.err == ""


def test_refuses_nonempty_output(tmp_path, capsys):
    output = tmp_path / "output"
    output.mkdir()
    (output / "keep.txt").write_text("original")
    assert main(draft_args(tmp_path)) == 1
    assert (output / "keep.txt").read_text() == "original"
    assert len(list(output.iterdir())) == 1
    assert "not empty" in capsys.readouterr().err


@pytest.mark.parametrize("extra,expected", [([], "2026-11-20"), (["--extended"], "2027-01-20")])
def test_deadline_command(capsys, extra, expected):
    assert main(["deadline", "--received", "2026-10-20", *extra]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == expected and len(lines) == 2


def test_every_command_without_network(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network access is forbidden.")

    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    assert main(draft_args(tmp_path)) == 0
    assert main(["deadline", "--received", "2026-10-20"]) == 0
    assert main(["deadline", "--received", "2026-10-20", "--extended"]) == 0
    assert main(["due", "--tracker", str(tmp_path / "output/tracker.csv")]) == 0


def test_invalid_file_never_reaches_argparse(tmp_path, capsys):
    path = tmp_path / "input.csv"
    path.write_text("PRIVATE_HEADER,contact\nPRIVATE_CELL,privacy@example.com\n")
    args = draft_args(tmp_path)
    args[2] = str(path)
    assert main(args) == 1
    result = capsys.readouterr()
    assert "PRIVATE" not in result.err and "row 1" in result.err
    assert result.out == "" and not (tmp_path / "output").exists()


def test_due_validates_all_rows_before_printing(tracker_file, capsys):
    path = tracker_file({}, {"status": "PRIVATE_CELL"})
    assert main(["due", "--tracker", str(path), "--today", "2026-11-21"]) == 1
    result = capsys.readouterr()
    assert result.out == "" and "PRIVATE_CELL" not in result.err
    assert "row 3" in result.err


@pytest.mark.parametrize(
    "arguments",
    [
        ["deadline", "--received", "PRIVATE_CELL"],
        ["due", "--tracker", "input.csv", "--today", "PRIVATE_CELL"],
    ],
)
def test_invalid_cli_date_is_redacted(capsys, arguments):
    with pytest.raises(SystemExit) as failure:
        main(arguments)
    assert failure.value.code == 1
    assert "PRIVATE_CELL" not in capsys.readouterr().err


def test_out_of_range_date(capsys):
    assert main(["deadline", "--received", "9999-12-31"]) == 1
    assert "out of range" in capsys.readouterr().err


def test_template_failure_writes_nothing(tmp_path, capsys):
    with patch("gdpr_erasure_kit.cli.render_request", side_effect=KeyError("PRIVATE_CELL")):
        assert main(draft_args(tmp_path)) == 1
    assert not (tmp_path / "output").exists()
    assert "PRIVATE_CELL" not in capsys.readouterr().err


def test_io_error_is_redacted(tmp_path, capsys):
    with patch("gdpr_erasure_kit.cli.exclusive_file", side_effect=OSError("PRIVATE_CELL")):
        assert main(draft_args(tmp_path)) == 1
    assert "PRIVATE_CELL" not in capsys.readouterr().err


def test_module_entrypoint(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["gdpr-kit", "deadline", "--received", "2026-10-20"])
    with pytest.raises(SystemExit) as failure:
        runpy.run_module("gdpr_erasure_kit", run_name="__main__")
    assert failure.value.code == 0
    assert "2026-11-20" in capsys.readouterr().out


def test_installed_console_script(tmp_path):
    name = "gdpr-kit.exe" if os.name == "nt" else "gdpr-kit"
    executable = Path(sys.executable).parent / name
    result = subprocess.run(  # noqa: S603 - installed entry point with synthetic fixtures.
        [str(executable), *draft_args(tmp_path), "--date", date(2026, 10, 20).isoformat()],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "5 drafts" in result.stdout


def test_tracker_write_failure_names_file_without_values(tmp_path, capsys):
    with patch("gdpr_erasure_kit.cli.write_tracker", side_effect=OSError("PRIVATE_CELL")):
        assert main(draft_args(tmp_path)) == 1
    error = capsys.readouterr().err
    assert "tracker.csv" in error and "row 1" in error
    assert "PRIVATE_CELL" not in error
