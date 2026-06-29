import sqlite3
from pathlib import Path
from typing import Any

from researchgraph.utils.dates import utc_now_iso


class RunStore:
    def __init__(self, db_path: str | Path = 'data/runs.sqlite') -> None:
        self.db_path =  Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def create_run(self, run_id: str, query: str) -> None:
        now = utc_now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO runs (run_id, query, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, query, "created", now, now),
            )

    def update_status(self, run_id: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE runs
                SET status = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (status, utc_now_iso(), run_id),
            )
        
    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f'Run not found: {run_id}')

        return dict(row)