from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class CRMStore:
    """PoC CRM store: persists cases to a local JSON file."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            self.db_path.write_text(json.dumps({"cases": []}, indent=2))

    def _read(self) -> dict:
        return json.loads(self.db_path.read_text())

    def _write(self, data: dict) -> None:
        self.db_path.write_text(json.dumps(data, indent=2))

    def create_case(self, member_id: str, agent_id: str, subject: str, note: str, metadata: dict | None = None) -> dict:
        data = self._read()
        cases = data.get("cases", [])
        case_id = f"C{len(cases)+1:05d}"
        case = {
            "case_id": case_id,
            "member_id": member_id,
            "agent_id": agent_id,
            "subject": subject,
            "note": note,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        cases.append(case)
        data["cases"] = cases
        self._write(data)
        return case

    def list_cases(self, member_id: str | None = None) -> list[dict]:
        cases = self._read().get("cases", [])
        if member_id:
            return [c for c in cases if c.get("member_id") == member_id]
        return cases

    def dump(self) -> dict:
        return self._read()
