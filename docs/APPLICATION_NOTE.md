# OVO Talent — AI Engineering Intern: short note + 2-minute demo

Copy / adapt this for the OVO form. Keep it short — the form asks
for a resume and a short note about something you built with AI.

---

Hi — I'm John Zuo, a CMU freshman (MCS, Biological Sciences,
computational biology track) in Pittsburgh, PA.

Something I built with AI: **Creator Outreach Assistant**
— GitHub link: [paste your repo URL here]

It's a small version of the tool you describe in the posting:
it sorts routine creator emails, drafts replies with GPT-6 Astra
at medium reasoning effort, extracts a structured creator profile
into a CRM, and — the part I spent most time on — runs
deterministic guardrails that catch invented rates, promised
payments, and leaked PII before a draft reaches a person.
It also has an evaluation harness: a 12-email golden set that
reports triage accuracy, guardrail pass rate, and latency, so
you can see whether a change actually made it better.

Python (FastAPI) on the back end, TypeScript for the demo UI,
tests with pytest, and it runs without an API key in mock mode
so a reviewer can try it in a minute.

Why this fits: I like the "measure what you ship" part of the
role. In a Kaggle dual-GPU project I learned the hard way that
"slow" and "stuck" look identical without logging — so in this
project I made the measurement the feature, not an afterthought.

I live in Pennsylvania, so I'm in one of the listed states for
the remote role, and I'm available part-time.

Thanks for considering me — John

---

## 2-minute demo script (for the screen recording)

0:00 — "This is Creator Outreach Assistant. It sorts creator
emails, drafts replies, and pulls info into a CRM."
0:15 — Run `python scripts/demo.py` — show triage = pricing,
draft, and CRM profile for the TikTok rate email.
0:45 — Run `pytest -q` and `python -m backend.evaluate` —
show the tests passing and the accuracy / guardrail numbers.
1:15 — Show the guardrail: paste a draft that invents a $900
rate into the checker, show it failing and going to human review.
1:40 — Show `backend/llm.py` — model `gpt-6-astra`, effort
`medium`, Responses API, tool calls `lookup_creator` /
`check_rate_card`; and `web/src/main.ts` for the TypeScript UI.
2:00 — "Code is on GitHub at [URL]. Happy to walk through it."

## GitHub upload — from this folder

```bash
cd creator-outreach-assistant
git init
git add .
git commit -m "Creator Outreach Assistant: triage, draft, guardrails, CRM extract, eval"
# create an empty repo on github.com first, then:
git remote add origin https://github.com/<your-username>/creator-outreach-assistant.git
git branch -M main
git push -u origin main
```

Do NOT commit a real `.env` or API key — `.gitignore` already
excludes `.env`. Check `git status` before pushing.
