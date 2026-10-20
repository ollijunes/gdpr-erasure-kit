import csv
import io
import os
from unittest.mock import patch

import pytest

from gdpr_erasure_kit.io import (
    InputError,
    escape_cell,
    exclusive_file,
    prepare_output,
    read_csv,
    read_identity,
    read_services,
    unescape_cell,
    valid_contact,
)


@pytest.mark.parametrize("prefix", ["=", "+", "-", "@", "\t", "\r"])
def test_csv_injection_round_trip(prefix):
    value = prefix + "synthetic value"
    escaped = escape_cell(value)
    assert escaped == "'" + value
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow([escaped])
    buffer.seek(0)
    assert unescape_cell(next(csv.reader(buffer))[0]) == value


@pytest.mark.parametrize("value", ["ordinary", "'ordinary", "'", "", "''=literal"])
def test_unescape_preserves_unrelated_quotes(value):
    assert unescape_cell(value) == value


def test_bom_blank_lines_and_optional_columns(services_file):
    path = services_file([[], ["", ""], ["Example", "privacy@example.org"]], bom=True)
    assert read_services(path) == [{"service": "Example", "contact": "privacy@example.org"}]


@pytest.mark.parametrize(
    "rows,header,number",
    [
        (
            [["Example", "privacy@example.org", "PRIVATE_CELL"]],
            ["service", "contact", "PRIVATE_HEADER"],
            1,
        ),
        ([["Example", "privacy@example.org"]], ["service", "service"], 1),
        ([["Example"]], ["service"], 1),
        ([["", "privacy@example.org"]], ["service", "contact"], 2),
        ([["PRIVATE_CELL", "private malformed contact"]], ["service", "contact"], 2),
        ([["Example", "privacy@example.org", "PRIVATE_CELL"]], ["service", "contact"], 2),
        ([["Example"]], ["service", "contact"], 2),
        (
            [["Example", "privacy@example.org", "PRIVATE_CELL"]],
            ["service", "contact", "request_type"],
            2,
        ),
        (
            [["Example", "privacy@example.org", "PRIVATE_CELL"]],
            ["service", "contact", "language"],
            2,
        ),
        ([["PRIVATE_CELL\x1b", "privacy@example.org"]], ["service", "contact"], 2),
        ([["PRIVATE_CELL\u202e", "privacy@example.org"]], ["service", "contact"], 2),
        (
            [["Example", "privacy@example.org"], [" example ", "privacy@example.net"]],
            ["service", "contact"],
            3,
        ),
        ([], ["service", "contact"], 1),
    ],
)
def test_invalid_service_input_is_redacted(services_file, rows, header, number):
    path = services_file(rows, header)
    with pytest.raises(InputError) as failure:
        read_services(path)
    message = str(failure.value)
    assert str(path) in message and f"row {number}:" in message
    assert "PRIVATE" not in message and "private malformed" not in message


@pytest.mark.parametrize("content", [b"", b"\xff", b'service,contact\n"PRIVATE_CELL'])
def test_invalid_csv_bytes(tmp_path, content):
    path = tmp_path / "input.csv"
    path.write_bytes(content)
    with pytest.raises(InputError):
        read_services(path)


def test_missing_csv(tmp_path):
    with pytest.raises(InputError, match="row 1"):
        read_services(tmp_path / "missing.csv")


def test_unescaped_formula_read(services_file):
    path = services_file([["'=Example", "privacy@example.org"]])
    assert read_services(path)[0]["service"] == "=Example"


@pytest.mark.parametrize(
    "contact,expected",
    [
        ("privacy@example.com", True),
        ("https://example.org/privacy", True),
        ("https://example.net:443/form?x=1", True),
        ("http://example.org/form", False),
        ("https://", False),
        ("https://example.org:invalid", False),
        ("https://alex@example.org/form", False),
        ("https://example.org/a b", False),
        ("https://example.org\\x", False),
        ("https://[broken", False),
        ("alex@", False),
        ("alex example@example.org", False),
        ("https://example.org:0", False),
    ],
)
def test_contact_validation(contact, expected):
    assert valid_contact(contact) is expected


@pytest.mark.parametrize(
    "content,number",
    [
        ('full_name = "Alex Example"\nemail = "PRIVATE_CELL"', 2),
        ('full_name = ""\nemail = "alex@example.com"', 1),
        ('email = "alex@example.com"', 1),
        ('full_name = ["PRIVATE_CELL"]\nemail = "alex@example.com"', 1),
        (
            'full_name = "Alex Example"\nemail = "alex@example.com"\n'
            'other_identifiers = "PRIVATE_CELL"',
            3,
        ),
        ('full_name = "Alex Example"\nemail = "alex@example.com"\nother_identifiers = [4]', 3),
        ('full_name = "Alex Example"\nemail = "alex@example.com"\npostal_address = 4', 3),
        ('full_name = "PRIVATE_CELL\\t"\nemail = "alex@example.com"', 1),
        (
            'full_name = "Alex Example"\nemail = "alex@example.com"\n'
            'PRIVATE_FIELD = "PRIVATE_CELL"',
            1,
        ),
        ('full_name = "Alex Example"\nemail = PRIVATE_CELL', 2),
    ],
)
def test_identity_errors_do_not_echo_values(tmp_path, content, number):
    path = tmp_path / "input.toml"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(InputError) as failure:
        read_identity(path)
    assert f"row {number}:" in str(failure.value)
    assert "PRIVATE" not in str(failure.value)


def test_missing_and_non_utf8_identity(tmp_path):
    path = tmp_path / "missing.toml"
    with pytest.raises(InputError):
        read_identity(path)
    path.write_bytes(b"\xff")
    with pytest.raises(InputError):
        read_identity(path)


def test_exclusive_create_and_private_modes(tmp_path):
    directory = tmp_path / "output"
    prepare_output(directory)
    path = directory / "request.txt"
    with exclusive_file(path) as stream:
        stream.write("original")
    with pytest.raises(InputError):
        exclusive_file(path)
    assert path.read_text() == "original"
    with pytest.raises(InputError, match="not empty"):
        prepare_output(directory)
    if os.name != "nt":
        assert directory.stat().st_mode & 0o777 == 0o700
        assert path.stat().st_mode & 0o777 == 0o600


def test_empty_existing_output_and_non_directory(tmp_path):
    prepare_output(tmp_path)
    path = tmp_path / "file"
    path.write_text("original")
    with pytest.raises(InputError):
        prepare_output(path)


@pytest.mark.skipif(os.name == "nt", reason="Symlinks may need extra Windows privileges.")
def test_symlink_output_refused(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(InputError):
        prepare_output(link)
    existing = target / "request.txt"
    existing.write_text("original")
    file_link = tmp_path / "request.txt"
    file_link.symlink_to(existing)
    with pytest.raises(InputError):
        exclusive_file(file_link)
    assert existing.read_text() == "original"


def test_permissions_failure_is_redacted(tmp_path):
    with patch("gdpr_erasure_kit.io.os.open", side_effect=PermissionError("PRIVATE_CELL")):
        with pytest.raises(InputError) as failure:
            exclusive_file(tmp_path / "request.txt")
    assert "PRIVATE_CELL" not in str(failure.value)


def test_csv_reports_start_of_multiline_record(tmp_path):
    path = tmp_path / "input.csv"
    path.write_text('service,contact\n\n"private\nvalue",privacy@example.org\n')
    with pytest.raises(InputError, match="row 3"):
        read_csv(path, ("service", "contact"), ("service", "contact"))
