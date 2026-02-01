from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    last_active_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    tool TEXT NOT NULL,
    symbols TEXT NOT NULL,
    verdict TEXT NOT NULL,
    advice TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    trace TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class Storage:
    def __init__(self, db_path: str | None = None) -> None:
        if db_path is None:
            db_path = _default_db_path()
        self.db_path = db_path
        self.init()

    def init(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def upsert_session(self, session_id: str) -> None:
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, created_at, last_active_at)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET last_active_at = excluded.last_active_at
                """,
                (session_id, now, now),
            )
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, _utc_now()),
            )
            conn.commit()

    def add_reading(
        self,
        session_id: str,
        tool: str,
        symbols: List[Dict[str, Any]],
        verdict: str,
        advice: List[str],
    ) -> None:
        payload_symbols = json.dumps(symbols, ensure_ascii=False)
        payload_advice = json.dumps(advice, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO readings (session_id, tool, symbols, verdict, advice, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, tool, payload_symbols, verdict, payload_advice, _utc_now()),
            )
            conn.commit()

    def add_trace(self, session_id: str, trace: List[Dict[str, Any]]) -> None:
        payload = json.dumps(trace, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO agent_traces (session_id, trace, created_at) VALUES (?, ?, ?)",
                (session_id, payload, _utc_now()),
            )
            conn.commit()

    def get_recent_messages(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        history = [
            {"role": row["role"], "content": row["content"], "created_at": row["created_at"]}
            for row in rows
        ]
        history.reverse()
        return history

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_db_path() -> str:
    env_path = os.getenv("ORACLE_CHOICE_DB_PATH")
    if env_path:
        return env_path

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    candidate = os.path.join(base_dir, "oracle_choice.db")
    if _dir_allows_delete(os.path.dirname(candidate)) and _file_is_writable(candidate):
        return candidate

    return os.path.join(tempfile.gettempdir(), "oracle_choice.db")


def _dir_allows_delete(directory: str) -> bool:
    test_path = os.path.join(directory, f".oracle_choice_write_test_{os.getpid()}")
    try:
        with open(test_path, "w", encoding="utf-8") as handle:
            handle.write("ok")
        os.remove(test_path)
        return True
    except OSError:
        return False


def _file_is_writable(path: str) -> bool:
    if not os.path.exists(path):
        return True
    return os.access(path, os.W_OK)
