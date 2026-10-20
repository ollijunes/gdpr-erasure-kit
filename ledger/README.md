# gdpr-erasure-kit

## Goal

Request templates for GDPR erasure (Article 17) and access (Article 15) in English and Finnish, a deadline tracker template and a standard-library Python CLI that turns a list of services into one request draft per service and a tracker file, for people who want to clean up their data across many services. A release is finished when the tests and ruff pass in CI, `scripts/check_public_tree.py` and gitleaks report nothing, and no real service, person, address or tracker row from anyone's own requests is in the repository history.

## Environments

Local only. `uv run pytest` and `uv run ruff check` run on the developer's machine; CI (`.github/workflows/ci.yml`) runs Linux, macOS and Windows with Python 3.11 to 3.14. The CLI never sends anything: it writes files that the user reviews and sends.

## Manual checks

Before a release, read every template in both languages against the current GDPR text (Articles 12, 15 and 17) and check that the article numbers, the one-month deadline and the extension rule are stated correctly. Generate drafts from `examples/services.example.csv` and open the tracker CSV in a spreadsheet: dates must be correct and no cell may start with a formula character.
