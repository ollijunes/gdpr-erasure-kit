from datetime import date
from unittest.mock import patch

import pytest

from gdpr_erasure_kit.io import InputError
from gdpr_erasure_kit.render import identifiers, render_request, slug


@pytest.mark.parametrize("language", ["en", "fi"])
@pytest.mark.parametrize("kind", ["erasure", "access"])
def test_all_templates(identity, service, language, kind):
    service.update(language=language, request_type=kind)
    result = render_request(identity, service, date(2026, 10, 20))
    assert "${" not in result
    assert "Alex Example" in result
    assert "Cloud Pebble" in result
    assert "customer number 12345" in result
    if language == "en":
        assert "20 October 2026" in result and "20 November 2026" in result
        assert "- Name: Alex Example" in result
        assert "- Email: alex@example.com" in result
        assert "- Account or username at your service: alex-example" in result
        assert "- Postal address: Example Street 1\n                  Example City" in result
        assert "- Other identifier:" in result
    else:
        assert "20.10.2026" in result and "20.11.2026" in result
        assert "- Nimi: Alex Example" in result
        assert "- Sähköposti: alex@example.com" in result
        assert "- Käyttäjätunnus tai tili palvelussanne: alex-example" in result
        assert "- Postiosoite:" in result and "- Muu tunniste:" in result


def test_substitution_is_single_pass(identity, service):
    service["service"] = "${full_name}"
    identity["postal_address"] = "${email}"
    result = render_request(identity, service, date(2026, 10, 20))
    assert "${full_name}" in result and "${email}" in result


def test_unknown_placeholder_fails(identity, service):
    with patch("gdpr_erasure_kit.render.files") as resource:
        resource.return_value.joinpath.return_value.read_text.return_value = "${unknown}"
        with pytest.raises(InputError, match="Invalid packaged template"):
            render_request(identity, service, date(2026, 10, 20))


def test_unreadable_template_error_is_redacted(identity, service):
    with patch("gdpr_erasure_kit.render.files") as resource:
        resource.return_value.joinpath.return_value.read_text.side_effect = OSError("PRIVATE_CELL")
        with pytest.raises(InputError) as failure:
            render_request(identity, service, date(2026, 10, 20))
    assert "row 1" in str(failure.value)
    assert "PRIVATE_CELL" not in str(failure.value)


def test_invalid_template_cannot_traverse(identity, service):
    service["language"] = "../"
    with pytest.raises(ValueError, match="Unsupported"):
        render_request(identity, service, date(2026, 10, 20))


def test_optional_identifiers_absent():
    result = identifiers({"full_name": "Alex Example", "email": "alex@example.com"}, "", "en")
    assert result.splitlines() == ["- Name: Alex Example", "- Email: alex@example.com"]


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Crème & Pöly", "creme-poly"),
        ("../../Example", "example"),
        ("東京", "service"),
        ("a" * 50, "a" * 40),
        ("a" * 39 + " ! b", "a" * 39),
    ],
)
def test_slug(value, expected):
    assert slug(value) == expected
