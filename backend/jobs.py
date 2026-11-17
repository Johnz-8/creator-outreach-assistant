"""Background jobs, in miniature.

OVO's work is not one request = one reply: routine mail is queued,
processed in the background, and measured. This module is a simple
in-memory queue with the same shape — enqueue, process, record
outcome — so the API can return fast and the LLM work happens
off the request path.

In production this would be Celery / RQ / a cloud queue. Here the
point is to show the pattern and to make it testable, not to ship
a queue server in a freshman portfolio project.
"""
from __future__ import annotations

import queue
import time
from dataclasses import dataclass, field


@dataclass
class Job:
    id: int
    kind: str  # "triage" | "draft" | "extract"
    payload: dict
    status: str = "queued"
    result: dict | None = None
    error: str | None = None
    started_at: float | None = None
    finished_at: float | None = None


class JobQueue:
    def __init__(self):
        self._q: queue.Queue[Job] = queue.Queue()
        self._jobs: dict[int, Job] = {}
        self._next = 1

    def enqueue(self, kind: str, payload: dict) -> Job:
        job = Job(id=self._next, kind=kind, payload=payload)
        self._next += 1
        self._jobs[job.id] = job
        self._q.put(job)
        return job

    def process_one(self, handler) -> Job | None:
        try:
            job = self._q.get_nowait()
        except queue.Empty:
            return None
        job.status = "running"
        job.started_at = time.time()
        try:
            job.result = handler(job)
            job.status = "done"
        except Exception as exc:  # noqa: BLE001 — record, don't crash the worker
            job.status = "failed"
            job.error = str(exc)
        job.finished_at = time.time()
        return job

    def get(self, job_id: int) -> Job | None:
        return self._jobs.get(job_id)

    def counts(self) -> dict:
        out = {"queued": 0, "running": 0, "done": 0, "failed": 0}
        for j in self._jobs.values():
            out[j.status] = out.get(j.status, 0) + 1
        return out
