from backend.extract import extract_creator


def test_followers_and_handle():
    out = extract_creator("Hi, I post science on TikTok @labnotes, 120k followers. Email me at a@example.com")
    assert out["handle"] == "labnotes"
    assert out["followers"] == 120000
    assert out["platform"] == "tiktok"
    assert out["email"] == "a@example.com"


def test_missing_fields_are_null_not_invented():
    out = extract_creator("Hi, just saying hello.")
    assert out["followers"] is None
    assert out["handle"] is None
    assert out["confidence"] == 0
