from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        return None
    return json.loads(path.read_text())


def load_member(member_id: str) -> dict:
    members = _load_json("members.json") or {}
    return members.get(member_id, {})


def load_claims(member_id: str) -> list[dict]:
    claims = _load_json("claims.json") or {}
    return claims.get(member_id, [])


def load_pa(member_id: str) -> list[dict]:
    pas = _load_json("prior_auth.json") or {}
    return pas.get(member_id, [])


def load_docs() -> list[dict]:
    return _load_json("docs.json") or []


def load_transcripts(member_id: str) -> list[dict]:
    transcripts = _load_json("transcripts.json") or {}
    return transcripts.get(member_id, [])
