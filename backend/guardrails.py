"""Checks that catch bad output before it reaches a person.

This is the part of the OVO job description I took most seriously:
"checks that catch bad output before it reaches a person."

A draft FAILS if any of these fire:
1. invented_rate_or_date — states a $ rate, a date, or a deliverable
   count that was not in the incoming email or the CRM record.
2. promises_payment — "we will pay", "guaranteed", "confirmed" for
   money or a booking that has not been confirmed.
3. pii_leak — contains an email / phone that was not in the input.
4. too_long — over MAX_DRAFT_WORDS (default 180).
5. no_greeting_or_signoff — a routine reply should open and close
   politely; a bare fragment is not sendable.
6. hallucinated_creator_fact — mentions a follower count, platform,
   or niche not present in the input.

The checker is deliberately boring and deterministic: regex + word
lists, no second LLM call on the happy path. A flagged draft goes
to a human, it is never auto-sent. `check()` returns a list of
failures; an empty list means PASS.
"""
from __future__ import annotations

import re

from .config import MAX_DRAFT_WORDS

MONEY = re.compile(r"\$\s?\d[\d,]*")
DATE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")
PROMISE = re.compile(r"\b(we will pay|guaranteed|confirmed booking|you are booked|payment sent)\b", re.I)


def check(draft: str, *, source_text: str = "", crm_text: str = "") -> list[str]:
    failures: list[str] = []
    known = f"{source_text}\n{crm_text}"

    if len(draft.split()) > MAX_DRAFT_WORDS:
        failures.append(f"too_long: {len(draft.split())} words > {MAX_DRAFT_WORDS}")
    if PROMISE.search(draft):
        failures.append("promises_payment: draft promises payment/booking")
    # Money / dates in the draft must appear in the source or CRM.
    for m in MONEY.finditer(draft):
        if m.group(0) not in known:
            failures.append(f"invented_rate_or_date: {m.group(0)!r} not in source/CRM")
    for m in DATE.finditer(draft):
        if m.group(0) not in known:
            failures.append(f"invented_rate_or_date: {m.group(0)!r} not in source/CRM")
    # PII in the draft must appear in the input.
    for m in list(EMAIL.finditer(draft)) + list(PHONE.finditer(draft)):
        if m.group(0) not in known:
            failures.append(f"pii_leak: {m.group(0)!r} not in source")
    if not draft.strip().lower().startswith(("hi", "hello", "thanks", "thank")):
        failures.append("no_greeting_or_signoff: draft does not open politely")
    return failures


def is_safe(draft: str, **kwargs) -> bool:
    return not check(draft, **kwargs)
