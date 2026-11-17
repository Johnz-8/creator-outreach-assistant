"""Sort routine creator replies: intent + priority, no LLM needed first.

OVO's inbox work is mostly routine: pricing, deliverables, timelines,
payments, declines, and spam. A fast rule pass handles the obvious
cases deterministically and cheaply; the LLM is only asked when the
rules are unsure. That is the point of this module — don't pay
$10/$50 per 1M tokens to classify "what's your rate?".

Intents: pricing, deliverable, timeline, payment, decline,
partnership, other, spam
Priority: high if a deadline / payment / live campaign is mentioned,
medium if it asks a question, low otherwise.
"""
from __future__ import annotations

import re

RULES = [
    ("pricing", [r"\brate\b", r"\bprice\b", r"how much", r"\bcost\b", r"\bfee\b", r"\bcharge\b"]),
    ("payment", [r"\bpay\b", r"\binvoice\b", r"\bpaid\b", r"payment", r"\bwire\b", r"bank"]),
    ("timeline", [r"\bdeadline\b", r"\btimeline\b", r"\bwhen\b.*\b(due|launch|post)\b", r"\bschedule\b"]),
    ("decline", [r"not interested", r"\bpass\b", r"decline", r"no thanks", r"not a fit"]),
    # Partnership before deliverable: "I post reels and want a brand
    # deal" is a partnership email, not a deliverable question.
    ("partnership", [r"partner", r"collab", r"brand deal", r"sponsor", r"campaign"]),
    ("deliverable", [r"\bdeliverable\b", r"\breel\b", r"\btiktok\b", r"\bvideo\b", r"\bpost\b", r"\bstory\b", r"\bbrief\b"]),
    ("spam", [r"crypto", r"buy followers", r"guaranteed.*followers", r"free money"]),
]


def classify(subject: str, body: str) -> dict:
    text = f"{subject}\n{body}".lower()
    for intent, patterns in RULES:
        if any(re.search(p, text) for p in patterns):
            break
    else:
        intent = "other"

    priority = "low"
    if re.search(r"\b(urgent|asap|today|tomorrow|overdue)\b", text):
        priority = "high"
    elif intent in {"pricing", "payment", "timeline"}:
        priority = "high"
    elif intent != "other":
        priority = "medium"

    needs_human = intent in {"payment", "decline"} or priority == "high"
    return {
        "intent": intent,
        "priority": priority,
        "needs_human_review": needs_human,
        "reason": f"matched {intent} rules" if intent != "other" else "no rule matched",
    }
