"""FastAPI service: triage, draft, extract, jobs, metrics.

Run:
    uvicorn backend.main:app --reload
    # then open http://127.0.0.1:8000/docs

Without OPENAI_API_KEY the LLM endpoints run in mock mode and say
so in every response. With a key they call gpt-6-astra at medium
reasoning effort (see backend/config.py).
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .config import MODEL, REASONING_EFFORT
from .crm import upsert_creator
from .draft import draft_reply
from .evaluate import run as run_eval
from .extract import extract_creator
from .jobs import JobQueue
from .triage import classify

app = FastAPI(title="Creator Outreach Assistant", version="0.1.0")
jobs = JobQueue()
METRICS = {"triage": 0, "draft": 0, "extract": 0, "guardrail_failures": 0}


class EmailIn(BaseModel):
    subject: str
    body: str
    creator_name: str = ""
    creator_handle: str = ""


class TextIn(BaseModel):
    text: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL, "effort": REASONING_EFFORT}


@app.get("/metrics")
def metrics():
    return {**METRICS, "jobs": jobs.counts()}


@app.post("/triage")
def triage(inp: EmailIn):
    METRICS["triage"] += 1
    return classify(inp.subject, inp.body)


@app.post("/draft")
def draft(inp: EmailIn):
    METRICS["draft"] += 1
    out = draft_reply(inp.subject, inp.body, creator_name=inp.creator_name)
    if out["guardrail_failures"]:
        METRICS["guardrail_failures"] += 1
    return out


@app.post("/extract")
def extract(inp: TextIn):
    METRICS["extract"] += 1
    profile = extract_creator(inp.text)
    saved = upsert_creator("data/crm.json", profile)
    return {"profile": profile, "saved": saved}


@app.post("/jobs/enqueue")
def enqueue(kind: str, inp: EmailIn):
    job = jobs.enqueue(kind, inp.model_dump())
    return {"job_id": job.id, "status": job.status}


@app.post("/jobs/process-one")
def process_one():
    def handler(job):
        p = job.payload
        if job.kind == "triage":
            return classify(p["subject"], p["body"])
        if job.kind == "draft":
            return draft_reply(p["subject"], p["body"])
        return extract_creator(p.get("body", ""))
    job = jobs.process_one(handler)
    return {"job_id": job.id, "status": job.status, "result": job.result} if job else {"done": False}


@app.get("/evaluate")
def evaluate():
    return run_eval(use_mock=True)
