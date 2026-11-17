"""Draft a routine reply, grounded in known facts only.

Prompt (the important part):
- You are writing for OVO Talent, a creator marketing company.
- Reply to THIS email only. Do not invent rates, dates, deliverables,
  follower counts, or promises.
- If the email asks for a rate or a date you do not have, say you
  will check and reply within 2 business days.
- Keep it under 180 words, warm, professional, no hype.

The function returns the draft plus the guardrail verdict. Callers
should never send a draft with failures — they go to a human.
"""
from __future__ import annotations

from .config import KNOWN_FACTS
from .guardrails import check
from .llm import complete

SYSTEM = (
    "You write routine replies for OVO Talent, a creator marketing company. "
    "Reply only to the email given. Never invent a rate, date, deliverable, "
    "follower count, or promise. If you do not know a rate or date, say you "
    "will check and reply within 2 business days. Keep it under 180 words, "
    "warm and professional."
)


def draft_reply(subject: str, body: str, *, creator_name: str = "",
                use_mock: bool | None = None) -> dict:
    user = (
        f"Creator: {creator_name or 'unknown'}\n"
        f"Subject: {subject}\nEmail:\n{body}\n\n"
        f"Known facts you may use: {KNOWN_FACTS}"
    )
    result = complete(SYSTEM, user, use_mock=use_mock)
    draft = result.text or "Thanks for reaching out — I will reply within 2 business days."
    failures = check(draft, source_text=f"{subject}\n{body}", crm_text=str(KNOWN_FACTS))
    return {
        "draft": draft,
        "provider": result.provider,
        "model": result.model,
        "effort": result.effort,
        "guardrail_failures": failures,
        "safe_to_send": not failures,
        "needs_human_review": bool(failures),
    }
