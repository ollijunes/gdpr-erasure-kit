"""Validated local inputs and exclusive private output files."""

import csv
import os
import re
import tomllib
import unicodedata
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TextIO
from urllib.parse import urlsplit

FORMULA_PREFIXES = "=+-@\t\r"
SERVICE_COLUMNS = ("service", "contact", "account_identifier", "request_type", "language", "notes")
REQUEST_TYPES = ("erasure", "access")
LANGUAGES = ("en", "fi")


class InputError(ValueError):
    def __init__(self, path: Path, row: int, reason: str):
        super().__init__(f"{str(path)!r}: row {row}: {reason}")


def has_controls(value: str, *, multiline: bool = False) -> bool:
    return any(
        unicodedata.category(char) in {"Cc", "Cf", "Cs"} and not (multiline and char == "\n")
        for char in value
    )


def valid_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^\s@<>(),;:\\\[\]\"]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", value))


def valid_contact(value: str) -> bool:
    if valid_email(value):
        return True
    if any(char.isspace() for char in value) or "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        return bool(
            parsed.scheme == "https"
            and parsed.hostname
            and not parsed.username
            and not parsed.password
            and parsed.port != 0
            and re.fullmatch(r"[A-Za-z0-9.-]+", parsed.hostname)
        )
    except ValueError:
        return False


def escape_cell(value: str) -> str:
    return "'" + value if value.startswith(tuple(FORMULA_PREFIXES)) else value


def unescape_cell(value: str) -> str:
    if len(value) > 1 and value[0] == "'" and value[1] in FORMULA_PREFIXES:
        return value[1:]
    return value


def read_csv(
    path: Path, columns: Sequence[str], required: Sequence[str]
) -> list[tuple[int, dict[str, str]]]:
    rows = []
    row_number = 1
    try:
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source, strict=True)
            header = next(reader, [])
            if (
                not header
                or len(set(header)) != len(header)
                or set(header) - set(columns)
                or set(required) - set(header)
            ):
                raise InputError(path, 1, "Invalid CSV header.")
            while True:
                row_number = reader.line_num + 1
                values = next(reader, None)
                if values is None:
                    break
                if not values or all(not value.strip() for value in values):
                    continue
                if len(values) != len(header):
                    raise InputError(path, row_number, "Incorrect number of CSV fields.")
                if any(has_controls(value) for value in values):
                    raise InputError(path, row_number, "Control characters are not allowed.")
                rows.append((row_number, dict(zip(header, values, strict=True))))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise InputError(path, row_number, "Cannot read valid UTF-8 CSV.") from exc
    return rows


def validate_service(row: Mapping[str, str], path: Path, number: int) -> None:
    if not row["service"].strip():
        raise InputError(path, number, "Service is required.")
    if not valid_contact(row["contact"]):
        raise InputError(path, number, "Contact must be an email or HTTPS URL.")
    if row.get("request_type") and row["request_type"] not in REQUEST_TYPES:
        raise InputError(path, number, "Invalid request type.")
    if row.get("language") and row["language"] not in LANGUAGES:
        raise InputError(path, number, "Invalid language.")


def read_services(path: Path) -> list[dict[str, str]]:
    result = []
    seen = set()
    for number, row in read_csv(path, SERVICE_COLUMNS, ("service", "contact")):
        validate_service(row, path, number)
        name = row["service"].strip().casefold()
        if name in seen:
            raise InputError(path, number, "Duplicate service name.")
        seen.add(name)
        result.append(row)
    if not result:
        raise InputError(path, 1, "No services found.")
    return result


def read_identity(path: Path) -> dict[str, str | list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise InputError(path, 1, "Cannot read UTF-8 identity file.") from exc
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        match = re.search(r"\(at line ([0-9]+), column [0-9]+\)$", str(exc))
        number = getattr(exc, "lineno", None) or (int(match[1]) if match else 1)
        raise InputError(path, number, "Invalid TOML.") from exc
    allowed = {"full_name", "email", "postal_address", "other_identifiers"}
    if data.keys() - allowed:
        raise InputError(path, 1, "Unknown identity field.")
    for key in allowed:
        number = next(
            (i for i, line in enumerate(text.splitlines(), 1) if re.match(rf"\s*{key}\s*=", line)),
            1,
        )
        value = data.get(key, [] if key == "other_identifiers" else "")
        values = value if key == "other_identifiers" and isinstance(value, list) else [value]
        if key == "other_identifiers" and not isinstance(value, list):
            raise InputError(path, number, "Other identifiers must be a list of strings.")
        if any(
            not isinstance(item, str) or has_controls(item, multiline=key == "postal_address")
            for item in values
        ):
            raise InputError(path, number, "Invalid identity field.")
        if key in {"full_name", "email"} and not value.strip():
            raise InputError(path, number, "Required identity field is missing.")
        if key == "email" and not valid_email(value):
            raise InputError(path, number, "Invalid identity email.")
    return data


def prepare_output(path: Path) -> None:
    try:
        if path.is_symlink():
            raise InputError(path, 1, "Output directory must not be a symbolic link.")
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        if os.name == "posix":
            if path.stat().st_uid != os.getuid():
                raise InputError(path, 1, "Output directory must be owned by the current user.")
            path.chmod(0o700)
        if any(path.iterdir()):
            raise InputError(path, 1, "Output directory is not empty.")
    except OSError as exc:
        raise InputError(path, 1, "Cannot prepare output directory.") from exc


def exclusive_file(path: Path) -> TextIO:
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        return os.fdopen(fd, "w", encoding="utf-8", newline="")
    except OSError as exc:
        raise InputError(path, 1, "Cannot create a new output file.") from exc
