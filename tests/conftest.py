import csv
from pathlib import Path

import pytest

from gdpr_erasure_kit.tracker import COLUMNS

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def identity():
    return {
        "full_name": "Alex Example",
        "email": "alex@example.com",
        "postal_address": "Example Street 1\nExample City",
        "other_identifiers": ["customer number 12345"],
    }


@pytest.fixture
def service():
    return {
        "service": "Cloud Pebble",
        "contact": "privacy@example.com",
        "account_identifier": "alex-example",
        "request_type": "erasure",
        "language": "en",
        "notes": "private fixture note",
    }


@pytest.fixture
def services_file(tmp_path):
    def write(rows, header=("service", "contact"), *, bom=False):
        path = tmp_path / "input.csv"
        with path.open("w", encoding="utf-8-sig" if bom else "utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        return path

    return write


@pytest.fixture
def tracker_file(tmp_path, service):
    def write(*rows):
        path = tmp_path / "input-tracker.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            for row in rows:
                values = {**service, "status": "sent", "sent_on": "2026-10-20", **row}
                writer.writerow({key: values.get(key, "") for key in COLUMNS})
        return path

    return write
