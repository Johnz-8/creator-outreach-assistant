"""Measure what you ship — evaluation harness.

Runs the golden set in data/golden.jsonl through triage + draft +
guardrails and reports, in plain numbers:
- triage accuracy (predicted intent vs labelled intent)
- guardrail pass rate (drafts with zero failures / all drafts)
- drafts needing human review
- mean draft length, mean latency (mock mode is fast; real mode
  is dominated by the API call, so latency is reported, not hidden)

Run:  python -m backend.evaluate
       python -m backend.evaluate --real   # uses the OpenAI API, costs money
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .draft import draft_reply
from .triage import classify

ROOT = Path(__file__).resolve().parent.parent


def run(use_mock: bool = True) -> dict:
    rows = [json.loads(l) for l in (ROOT / "data" / "golden.jsonl").read_text().splitlines() if l.strip()]
    correct = 0
    safe = 0
    need_human = 0
    lengths: list[int] = []
    latencies: list[float] = []
    for row in rows:
        t0 = time.time()
        got = classify(row["subject"], row["body"])
        out = draft_reply(row["subject"], row["body"], use_mock=use_mock)
        latencies.append(time.time() - t0)
        if got["intent"] == row["intent"]:
            correct += 1
        if out["safe_to_send"]:
            safe += 1
        if out["needs_human_review"]:
            need_human += 1
        lengths.append(len(out["draft"].split()))
    return {
        "n": len(rows),
        "triage_accuracy": round(correct / len(rows), 3) if rows else 0,
        "guardrail_pass_rate": round(safe / len(rows), 3) if rows else 0,
        "needs_human_review": need_human,
        "mean_draft_words": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "mean_latency_s": round(sum(latencies) / len(latencies), 3) if latencies else 0,
        "provider": "mock" if use_mock else "openai",
        "model": "gpt-6-astra",
        "effort": "medium",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", action="store_true", help="use the OpenAI API (costs money)")
    args = ap.parse_args()
    print(json.dumps(run(use_mock=not args.real), indent=2))
