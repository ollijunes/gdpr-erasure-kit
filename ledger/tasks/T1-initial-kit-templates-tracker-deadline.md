# T1 Initial kit: templates, tracker, deadline guide and draft CLI

- Status: done
- Lane: feat/initial-kit-20261020
- Evidence: CI 15/15 on Linux, macOS and Windows with Python 3.11–3.14, lint, secrets and ledger: https://github.com/ollijunes/gdpr-erasure-kit/actions/runs/39435700902

## Plan

Goal: erasure and access templates in English and Finnish, a tracker template, deadline and Google Sheets guides, and a standard-library CLI (`draft`, `due`, `deadline`) with tests, CI and a privacy scan.

Checks: pytest with 90 % coverage, ruff check and format, `scripts/check_public_tree.py`, gitleaks over the full history, an end-to-end run with the example files.
