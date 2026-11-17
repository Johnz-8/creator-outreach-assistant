from backend.guardrails import check, is_safe


def test_invented_rate_fails():
    failures = check("Hi! We will pay you $900 for this.", source_text="Hi, what is your rate?")
    assert any("invented_rate" in f for f in failures)


def test_promise_fails():
    failures = check("Hi! We will pay you soon.", source_text="Hi")
    assert any("promises_payment" in f for f in failures)


def test_safe_draft_passes():
    draft = "Hi! Thanks for sharing your rates — I will check them and reply within 2 business days."
    assert is_safe(draft, source_text="My rate is $450")


def test_too_long_fails():
    draft = "Hi! " + "word " * 200
    assert any("too_long" in f for f in check(draft, source_text="Hi"))
