# Security

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/ollijunes/gdpr-erasure-kit/security/advisories/new).
Do not open a public issue that contains your identity file, your list of
services, a generated draft or a tracker row. Describe the problem with
invented data and include the affected version. Security fixes target the
latest release.

## What the tool handles

Your identity file, your services list, the drafts and the tracker are
personal data. Together they show which services you use and what you asked
them. The tool is built so that this data stays in files you control.

- No network. The tool does not send email, submit forms or contact any
  service. A test runs every command with network sockets disabled.
- Files you review. Drafts are plain text. You read each one and send it
  yourself.
- Private output. On Linux and macOS the output directory is created with mode
  `700` and each file with mode `600`. The tool refuses to write into a
  directory that is not empty and never overwrites an existing file.
- Quiet errors. Error messages name the file and row number, not the cell
  value. The summary prints counts and the output folder, not your name or
  email address.
- Spreadsheet safety. A tracker cell that would start with `=`, `+`, `-`, `@`,
  a tab or a carriage return is written with a leading `'`, so a spreadsheet
  shows it as text instead of running it as a formula.
- Templates are filled with Python's `string.Template`. A value that contains
  `${...}` stays literal text and cannot pull in other fields.

## What it does not protect

- Windows does not use POSIX file modes. Keep the output folder in a location
  only your account can read.
- The tool does not encrypt anything. Use disk encryption, and keep the files
  out of shared or synced folders you do not control.
- Once you send a request, its content is with the service and your email
  provider. The tool cannot change that.
- It does not check that a contact address really belongs to the service.
  Take privacy contacts from the service's own privacy notice.

## Repository hygiene

Examples use invented people and services on `example.com`, `example.org` and
`example.net`. No real service list, request, reply or tracker row belongs in
this repository, not even in a temporary commit.

CI scans the full Git history with Gitleaks and with
`scripts/check_public_tree.py`. The second script looks for private network
addresses, home-directory paths, email addresses outside the example domains,
Finnish personal identity codes and phone numbers, and private working files
such as `identity.toml` or `tracker.csv`. Synthetic canaries test its
patterns. Automated scans support a manual review; they do not prove that
nothing private slipped in.
