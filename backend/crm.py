"""Tiny JSON-file CRM store. No database needed for a demo repo.

A real production CRM would be Postgres; for a portfolio project a
JSON file keeps the whole thing runnable with `python -m uvicorn`
and no setup, and it makes the "pull info into the CRM" step visible:
`upsert_creator()` writes exactly what `extract_creator()` found,
with nulls preserved, never invented.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def load(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def save(path: str, creators: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(creators, indent=2))


def upsert_creator(path: str, profile: dict) -> dict:
    creators = load(path)
    key = profile.get("handle") or profile.get("email")
    for i, c in enumerate(creators):
        if key and (c.get("handle") == key or c.get("email") == key):
            creators[i] = {**c, **{k: v for k, v in profile.items() if v is not None}}
            save(path, creators)
            return creators[i]
    creators.append(profile)
    save(path, creators)
    return profile
