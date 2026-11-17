"""Pull structured creator info from an email / web snippet into CRM form.

This is the third OVO task in miniature: "pull information from the
web into our CRM." The extractor is deterministic (regex + lists),
so its output is testable. An LLM draft that invents a follower count
is a guardrail failure; an extractor that invents one is worse, so
this module never guesses — a field it cannot find is null, with
`confidence` lowered accordingly.

Fields: name, handle, platform, niche, followers, email, rate_hint,
links. `followers` is parsed from "120k", "1.2M", "120,000", etc.
"""
from __future__ import annotations

import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HANDLE = re.compile(r"@([A-Za-z0-9._]{2,30})")
URL = re.compile(r"https?://[^\s)>\"]+")
FOLLOWERS = re.compile(r"(\d+(?:\.\d+)?)\s*([kKmM])\b|(\d{1,3}(?:,\d{3})+)\s*(?:followers|subs)?", re.I)
PLATFORMS = ["tiktok", "instagram", "youtube", "twitch", "x", "twitter"]
NICHES = ["science", "biology", "fitness", "beauty", "gaming", "food", "tech", "travel", "finance"]


def _followers(text: str) -> int | None:
    m = FOLLOWERS.search(text)
    if not m:
        return None
    if m.group(3):
        return int(m.group(3).replace(",", ""))
    num, suffix = float(m.group(1)), m.group(2).lower()
    return int(num * 1000) if suffix == "k" else int(num * 1_000_000)


def extract_creator(text: str) -> dict:
    low = text.lower()
    email_m = EMAIL.search(text)
    handle_m = HANDLE.search(text)
    platform = next((p for p in PLATFORMS if p in low), None)
    niche = next((n for n in NICHES if n in low), None)
    followers = _followers(text)
    links = URL.findall(text)

    found = sum(x is not None for x in [email_m, handle_m, platform, followers])
    handle = handle_m.group(1).rstrip(".") if handle_m else None
    return {
        "name": None,  # names are not guessed from free text
        "handle": handle,
        "email": email_m.group(0) if email_m else None,
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "links": links,
        "confidence": round(found / 4, 2),
        "source": "email_or_web_snippet",
    }
