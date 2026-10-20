from scripts import check_public_tree as scan


def test_scanner_canaries():
    scan.self_test()


def test_github_merge_committer_email_exception_is_exact():
    assert not scan.detect(b"GitHub <noreply@github.com>")
    for local, domain in (
        (b"someone", b"github.com"),
        (b"other-noreply", b"github.com"),
        (b"noreply", b"github.com.unapproved"),
        (b"noreply", b"sub.github.com"),
    ):
        assert "non-example email address" in scan.detect(local + b"@" + domain)


def test_email_allowlist_does_not_match_domain_prefixes():
    for domain in (
        b"example.com",
        b"example.org",
        b"example.net",
        b"sub.example.invalid",
        b"sub.example.test",
        b"sub.example.example",
        b"users.noreply.github.com",
        b"anthropic.com",
    ):
        assert not scan.detect(b"synthetic@" + domain)
    for domain in (b"example.com.unapproved", b"unapproved.com"):
        assert "non-example email address" in scan.detect(b"synthetic@" + domain)


def test_personal_code_checks_calendar_and_checksum():
    def code(digits, separator):
        check = scan.CHECK_CHARACTERS[int(digits) % 31 : int(digits) % 31 + 1]
        return digits[:6] + separator + digits[6:] + check

    assert "Finnish personal identity code" in scan.detect(code(b"290200" + b"123", b"A"))
    assert "Finnish personal identity code" not in scan.detect(code(b"290200" + b"123", b"-"))
    assert "Finnish personal identity code" not in scan.detect(code(b"320100" + b"123", b"A"))


def test_private_files_and_examples():
    for filename in (
        "identity.toml",
        "data/services.csv",
        "out/tracker.csv",
        "drafts/note.txt",
        "data/drafts/note.txt",
        "data/.env.production",
        "request.key",
    ):
        assert scan.private_path(filename)
    for filename in (
        "tracker/tracker-template.csv",
        "examples/identity.example.toml",
        "examples/services.example.csv",
        "gdpr_erasure_kit/templates/en/access.txt",
    ):
        assert not scan.private_path(filename)
