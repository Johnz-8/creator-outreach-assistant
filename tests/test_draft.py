from backend.draft import draft_reply


def test_mock_draft_is_safe_and_labelled():
    out = draft_reply("My rate", "My rate for one TikTok is $450", use_mock=True)
    assert out["provider"] == "mock"
    assert out["model"] == "gpt-6-astra"
    assert out["effort"] == "medium"
    assert out["draft"]
    assert out["safe_to_send"] is True


def test_jobs_queue():
    from backend.jobs import JobQueue

    q = JobQueue()
    job = q.enqueue("triage", {"subject": "Hi", "body": "My rate is $100"})
    done = q.process_one(lambda j: {"ok": True})
    assert done is not None and done.status == "done"
    assert q.get(job.id).status == "done"
