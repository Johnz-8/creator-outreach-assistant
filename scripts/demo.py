"""Demo without a server or API key: triage + draft + extract, mock LLM.

Run:  python scripts/demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.draft import draft_reply
from backend.extract import extract_creator
from backend.triage import classify

EMAIL = {
    "subject": "My rate for a TikTok",
    "body": "Hi! My rate for one TikTok is $450. I post science explainers, "
            "120k followers on TikTok @labnotes. Let me know if that works.",
}

if __name__ == "__main__":
    print("triage:", classify(EMAIL["subject"], EMAIL["body"]))
    print("draft:", draft_reply(EMAIL["subject"], EMAIL["body"], use_mock=True))
    print("crm:", extract_creator(EMAIL["body"]))
