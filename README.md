# Creator Outreach Assistant

A small, honest AI assistant for a creator marketing inbox — the kind of
tool OVO Talent builds for itself.

It does the three things in the OVO AI Engineering Intern description,
in one runnable project:

1. **Sort routine replies** — classify a creator email by intent
   (pricing, deliverable, timeline, payment, decline, partnership,
   spam) and priority, with a human-review flag.
2. **Draft replies** — draft a routine reply with an LLM, grounded
   only in facts from the email or the CRM.
3. **Pull info into the CRM** — extract a structured creator profile
   (handle, platform, niche, followers, email, links) from free text
   and save it to a JSON CRM store. Missing fields stay `null` —
   they are never invented.

And the part that matters most for production use:

4. **Guardrails that catch bad output before it reaches a person.**
   A draft fails if it invents a rate or date, promises payment,
   leaks PII that was not in the input, or runs too long. Flagged
   drafts go to a human; they are never auto-sent.
5. **Measure what you ship.** `python -m backend.evaluate` runs a
   12-email golden set and reports triage accuracy, guardrail pass
   rate, drafts needing human review, mean draft length and latency.

## Model: GPT-6 Astra, medium effort

- Model ID: `gpt-6-astra`
- Reasoning effort: `medium`
- API: OpenAI Responses API (`POST /v1/responses`), with function
  tools `lookup_creator` and `check_rate_card`.

Medium is deliberate. Astra's effort ladder is low / medium / high /
xhigh / max, and medium is the default sweet spot — strong enough
for short inbox emails, without paying max-effort prices on every
routine reply. Astra is $10 / $50 per 1M input / output tokens.
High effort is reserved in the code for one case only: a second
pass on a draft a guardrail already flagged.

## Run it — no API key needed

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Demo, no server, no key (mock LLM, labelled as mock)
python scripts/demo.py

# 2. Tests
pytest -q

# 3. Evaluation on the golden set
python -m backend.evaluate

# 4. API server
uvicorn backend.main:app --reload
# open http://127.0.0.1:8000/docs
# POST /triage, /draft, /extract, /jobs/enqueue, GET /metrics, /evaluate
```

With a key, set it in `.env` (see `.env.example`) and the same
endpoints call the real API. **Note:** a ChatGPT subscription —
including CMU ChatGPT Edu — does not pay for API calls. API billing
is separate, so this project runs in mock mode by default and never
charges you silently.

## TypeScript frontend

`web/` is a small TypeScript UI that calls the same API — paste an
email, see triage, the draft, the guardrail verdict, and the CRM
profile. Nothing is sent.

```bash
cd web
npm install
npm run build   # tsc -> dist/
# open index.html (serve it, e.g. npx serve .) with the API running
```

## How it works

```
email ──► triage.py (rules first, LLM only when unsure)
      ──► draft.py  (GPT-6 Astra, medium, grounded prompt)
      ──► guardrails.py (deterministic checks, PASS / human review)
      ──► extract.py + crm.py (structured profile → data/crm.json)
      ──► jobs.py (background queue: enqueue → process → record)
      ──► evaluate.py (golden set → accuracy / pass rate / latency)
```

Why rules first for triage? Don't pay flagship-model prices to
classify "what's your rate?". The LLM is for drafting, where
language actually matters — and even there, the guardrail is
deterministic regex, not a second LLM call, so a bad draft can't
talk its way past the checker.

## Evaluation (mock mode, 12-email golden set)

Run it yourself — the numbers below are from the run in this repo,
not a claim:

```
$ python -m backend.evaluate
{
  "n": 12,
  "triage_accuracy": 1.0,
  "guardrail_pass_rate": 1.0,
  "needs_human_review": 0,
  "mean_draft_words": 22.9,
  "mean_latency_s": 0.0,
  "provider": "mock",
  "model": "gpt-6-astra",
  "effort": "medium"
}
$ pytest -q
11 passed
```

It reports `triage_accuracy`, `guardrail_pass_rate`,
`needs_human_review`, `mean_draft_words`, and `mean_latency_s`.
Mock mode is fast and free; real-API mode is slower and costs
tokens, which is itself a measurement worth reporting.

## What I would do next

- Add a real web-search tool for `lookup_creator`, so a handle
  with no CRM record can be enriched from a public profile — with
  the source URL stored next to every extracted fact.
- Log every guardrail failure with the draft and the input, so
  the prompt and the rules improve from real failures, not guesses.
- Add a second evaluation set written from real (anonymised)
  replies, and track accuracy over time in `/metrics`.

## About me

I'm John Zuo, a first-year at Carnegie Mellon — Mellon College of
Science, Biological Sciences, on the computational biology transfer
track. My coursework so far is Honors Modern Biology, chemistry
(09-106), and 15-112 (Python). I also run a small faculty research
focus group (03-210), where the work is reading papers and pulling
structured summaries out of unstructured text — the same skill this
project uses for CRM extraction, just in a different domain.

Outside class I built and debugged a dual-GPU image-generation
pipeline on Kaggle (two T4s, CPU offload, per-step logging to tell
"slow" from "stuck"), which is where I learned to measure a model
system instead of trusting that it worked.

I live in Pittsburgh, Pennsylvania — one of the states listed for
this remote internship — and I'm applying for the part-time AI
Engineering Intern role.

## Licence

MIT — see `LICENSE`.
