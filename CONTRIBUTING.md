# Contributing

Bug reports, corrections to the templates and new languages are welcome.
Keep changes focused and add a test when behaviour changes.

```sh
uv sync --locked
uv run python -m pytest --cov=gdpr_erasure_kit --cov-fail-under=90
uv run ruff check .
uv run ruff format --check .
gitleaks git --redact --no-banner .
python3 scripts/check_public_tree.py
```

## Templates

The templates are in `gdpr_erasure_kit/templates/<language>/`. A change to a
template should say which article or guideline it relies on. Keep the
language plain: short sentences, the article number next to each demand, no
threats.

To add a language, copy both English templates into a new folder, translate
them with the official terms of the GDPR in that language, and add the labels
and date format in the code. Say in the pull request who checked the legal
terms.

## Personal data

Tests and examples use invented people and services on `example.com`,
`example.org` and `example.net`. Never add your own identity file, services
list, drafts, tracker, or a reply you received from a service, even to a
temporary commit. Bug reports should use the example files.

Runtime code stays standard-library-only and does not open network
connections. Do not add a feature that sends requests on the user's behalf.

Use a public-safe Git author address. Report vulnerabilities through
[SECURITY.md](SECURITY.md), not a public issue.

## Not legal advice

The kit helps you write and track requests. It is not legal advice, and a pull
request that turns it into a claim of legal certainty will be declined.
