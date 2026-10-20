"""Render packaged templates with a single substitution pass."""

import re
import unicodedata
from datetime import date
from importlib.resources import files
from pathlib import Path
from string import Template

from .dates import deadline, localized
from .io import InputError

LABELS = {
    "en": (
        "Name",
        "Email",
        "Account or username at your service",
        "Postal address",
        "Other identifier",
    ),
    "fi": (
        "Nimi",
        "Sähköposti",
        "Käyttäjätunnus tai tili palvelussanne",
        "Postiosoite",
        "Muu tunniste",
    ),
}


def slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")[:40].rstrip("-") or "service"


def identifiers(identity: dict, account: str, language: str) -> str:
    labels = LABELS[language]
    entries = [
        (labels[0], identity["full_name"]),
        (labels[1], identity["email"]),
        (labels[2], account),
        (labels[3], identity.get("postal_address", "")),
        *((labels[4], value) for value in identity.get("other_identifiers", [])),
    ]
    bullets = []
    for label, value in entries:
        if value:
            prefix = f"- {label}: "
            bullets.append(prefix + value.replace("\n", "\n" + " " * len(prefix)))
    return "\n".join(bullets)


def render_request(identity: dict, service: dict, request_date: date) -> str:
    language, kind = service["language"], service["request_type"]
    if language not in LABELS or kind not in {"erasure", "access"}:
        raise ValueError("Unsupported template.")
    template = files("gdpr_erasure_kit").joinpath("templates", language, f"{kind}.txt")
    try:
        content = template.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        path = Path("gdpr_erasure_kit/templates") / language / f"{kind}.txt"
        raise InputError(path, 1, "Cannot read packaged template.") from exc
    return Template(content).substitute(
        service_name=service["service"],
        date=localized(request_date, language),
        identifiers=identifiers(identity, service.get("account_identifier", ""), language),
        deadline=localized(deadline(request_date), language),
        full_name=identity["full_name"],
    )
