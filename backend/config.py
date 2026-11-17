"""Configuration for creator-outreach-assistant.

Model choice is deliberate, not a default:
- Model: gpt-6-astra (OpenAI, Responses API)
- Reasoning effort: medium

Why medium? OpenAI's effort ladder is low / medium / high / xhigh / max,
and medium is the documented sweet spot for most work — it beats the
previous flagship at max effort while costing less per task. Astra is
$10 / $50 per 1M input / output tokens, so running everything at max
would be wasteful for short inbox emails. High / max are reserved in
this codebase for one place only: a second-pass check on a draft that
a guardrail already flagged.

If OPENAI_API_KEY is not set, the app runs in mock mode. That is
intentional: a reviewer can run the whole demo, the tests and the
evaluation without paying for API calls, and without a key. Mock mode
is labelled as mock everywhere it appears in output.
"""
from __future__ import annotations

import os

MODEL = os.environ.get("OPENAI_MODEL", "gpt-6-astra")
REASONING_EFFORT = os.environ.get("OPENAI_REASONING_EFFORT", "medium")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
MAX_DRAFT_WORDS = int(os.environ.get("MAX_DRAFT_WORDS", "180"))
CRM_PATH = os.environ.get("CRM_PATH", "data/crm.json")

# Facts the assistant is allowed to state in a draft. Anything not in
# this list, or not in the incoming email itself, must not be invented.
# This is the guardrail's source of truth.
KNOWN_FACTS = {
    "company": "OVO Talent",
    "company_what": "a creator marketing company",
    "reply_time": "within 2 business days",
    "next_step": "a short intro call",
}
