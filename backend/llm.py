"""LLM client: OpenAI Responses API, with a deterministic mock fallback.

Real path
---------
POST {base}/responses with:
  model: gpt-6-astra
  reasoning: {"effort": "medium"}
  input: a list of role/content messages
  tools: function tools the model may call (see TOOLS below)

The Responses API is the right call here, not Chat Completions:
it is the API OpenAI documents for tool use with this model family,
and it returns structured tool calls in one place.

Mock path
---------
If no OPENAI_API_KEY is set, or the caller passes use_mock=True,
no network call is made. The mock returns a short, clearly-labelled
draft / classification based on keywords in the prompt. Tests and
the demo use the mock, so `pytest` and `python scripts/demo.py`
work offline. Every mock response includes "provider": "mock".

No secret is ever logged. The key is read only from the environment.
"""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field

from .config import MODEL, OPENAI_API_KEY, OPENAI_BASE_URL, REASONING_EFFORT

TOOLS = [
    {
        "type": "function",
        "name": "lookup_creator",
        "description": "Look up a creator in the CRM by handle or email. Returns the stored profile, or null.",
        "parameters": {
            "type": "object",
            "properties": {
                "handle": {"type": "string"},
                "email": {"type": "string"},
            },
        },
    },
    {
        "type": "function",
        "name": "check_rate_card",
        "description": "Check the stored rate card for a creator / deliverable. Never invent a rate.",
        "parameters": {
            "type": "object",
            "properties": {
                "handle": {"type": "string"},
                "deliverable": {"type": "string"},
            },
        },
    },
]


@dataclass
class LLMResult:
    text: str
    provider: str  # "openai" or "mock"
    model: str = MODEL
    effort: str = REASONING_EFFORT
    tool_calls: list = field(default_factory=list)
    usage: dict = field(default_factory=dict)


def _mock_reply(system: str, user: str) -> str:
    low = user.lower()
    if "rate" in low or "price" in low or "how much" in low:
        return (
            "Thanks for sharing your rates — I will check them against the "
            "brief and come back within 2 business days with next steps."
        )
    if "decline" in low or "not interested" in low or "pass" in low:
        return (
            "Thanks for letting us know — no worries at all, and we will "
            "keep you in mind for a future fit."
        )
    if "timeline" in low or "when" in low or "deadline" in low:
        return (
            "Thanks for the timeline note — I will confirm the dates with "
            "the team and reply within 2 business days."
        )
    return (
        "Thanks for reaching out — I would love to learn more about your "
        "content and audience, and I will reply within 2 business days."
    )


def complete(system: str, user: str, *, use_mock: bool | None = None,
             effort: str | None = None) -> LLMResult:
    """One LLM call. Returns text, provider, and any tool calls."""
    if use_mock is None:
        use_mock = not bool(OPENAI_API_KEY)
    if use_mock:
        return LLMResult(text=_mock_reply(system, user), provider="mock")

    payload = {
        "model": MODEL,
        "reasoning": {"effort": effort or REASONING_EFFORT},
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "tools": TOOLS,
    }
    req = urllib.request.Request(
        f"{OPENAI_BASE_URL.rstrip('/')}/responses",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())

    # Responses API: output is a list of items; collect text + tool calls.
    texts, calls = [], []
    for item in body.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    texts.append(part.get("text", ""))
        elif item.get("type") == "function_call":
            calls.append({"name": item.get("name"), "arguments": item.get("arguments", "")})
    return LLMResult(
        text="\n".join(texts).strip(),
        provider="openai",
        tool_calls=calls,
        usage=body.get("usage", {}),
    )
