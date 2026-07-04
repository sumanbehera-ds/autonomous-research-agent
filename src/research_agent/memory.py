from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from research_agent.utils import ensure_directory, utc_now_iso


@dataclass
class ResearchMemory:
    db_path: Path = Path(".agent_memory/research_history.sqlite3")

    def __post_init__(self) -> None:
        ensure_directory(self.db_path.parent)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    report_path TEXT NOT NULL,
                    pdf_path TEXT,
                    report_preview TEXT NOT NULL
                )
                """
            )

    def save_run(
        self,
        *,
        topic: str,
        plan: dict[str, Any],
        sources: list[dict[str, Any]],
        report_path: str,
        pdf_path: str | None,
        report_preview: str,
    ) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO research_runs (
                    created_at, topic, plan_json, sources_json,
                    report_path, pdf_path, report_preview
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    topic,
                    json.dumps(plan, ensure_ascii=False),
                    json.dumps(sources, ensure_ascii=False),
                    report_path,
                    pdf_path,
                    report_preview,
                ),
            )
            return int(cursor.lastrowid)

    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, topic, report_path, pdf_path, report_preview
                FROM research_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_run(self, run_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM research_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None

        data = dict(row)
        data["plan"] = json.loads(data.pop("plan_json"))
        data["sources"] = json.loads(data.pop("sources_json"))
        return data
