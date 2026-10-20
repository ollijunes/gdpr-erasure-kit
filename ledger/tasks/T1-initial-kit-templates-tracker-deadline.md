# T1 Initial kit: templates, tracker, deadline guide and draft CLI

- Status: doing
- Lane: feat/initial-kit-20261020
- Evidence: —

## Plan

Goal: erasure and access templates in English and Finnish, a tracker template, deadline and Google Sheets guides, and a standard-library CLI (`draft`, `due`, `deadline`) with tests, CI and a privacy scan.

Checks: pytest with 90 % coverage, ruff check and format, `scripts/check_public_tree.py`, gitleaks over the full history, an end-to-end run with the example files.
