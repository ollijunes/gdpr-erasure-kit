# T1 Initial kit: templates, tracker, deadline guide and draft CLI

- Status: doing
- Lane: feat/initial-kit-20261020
- Evidence: —

## Plan

Goal: erasure and access templates in English and Finnish, a tracker template, deadline and Google Sheets guides, and a standard-library CLI (`draft`, `due`, `deadline`) with tests, CI and a privacy scan.

Checks: pytest with 90 % coverage, ruff check and format, `scripts/check_public_tree.py`, gitleaks over the full history, an end-to-end run with the example files.

## Handoff

Local checks on macOS with Python 3.12 pass: 160 tests at 100 % coverage, ruff, Gitleaks over the full history, `scripts/check_public_tree.py` with 0 findings, an end-to-end run with the example files, and the Codex second review with its blocking finding fixed. The verify stamp is in `ledger/verified/`.

The first push was refused because the GitHub token lacks the `workflow` scope. Next: once the owner has refreshed the token, push the branch, open the pull request, confirm CI on Linux, macOS and Windows, then set Status: done.
