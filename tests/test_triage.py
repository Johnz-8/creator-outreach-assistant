from backend.triage import classify


def test_pricing():
    assert classify("My rate", "My rate for one TikTok is $450")["intent"] == "pricing"


def test_payment_is_high_priority():
    out = classify("Invoice", "Attaching my invoice, payment overdue")
    assert out["intent"] == "payment"
    assert out["priority"] == "high"
    assert out["needs_human_review"] is True


def test_other_when_no_rule_matches():
    assert classify("Hello", "Just saying hi, hope you are well")["intent"] == "other"
