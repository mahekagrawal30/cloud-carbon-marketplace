"""SQLite storage for carbon-credit transactions."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import uuid


def _connect(db_path: str | Path) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def initialize_database(db_path: str | Path) -> None:
    with _connect(db_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS simulated_transactions (
            transaction_id TEXT PRIMARY KEY, certificate_id TEXT NOT NULL, project_id TEXT NOT NULL,
            project_name TEXT NOT NULL, credits REAL NOT NULL, price_per_tonne REAL NOT NULL,
            total_price REAL NOT NULL, offset_tonnes REAL NOT NULL, purchased_at TEXT NOT NULL
        )""")


def record_transaction(db_path: str | Path, project: dict, credits: float) -> dict:
    transaction_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
    certificate_id = f"CCFM-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    total = round(float(credits) * float(project["price_per_tonne"]), 2)
    record = {"transaction_id": transaction_id, "certificate_id": certificate_id, "project_id": project["project_id"],
              "project_name": project["name"], "credits": round(float(credits), 3), "price_per_tonne": float(project["price_per_tonne"]),
              "total_price": total, "offset_tonnes": round(float(credits), 3), "purchased_at": datetime.now(timezone.utc).isoformat()}
    with _connect(db_path) as conn:
        conn.execute("""INSERT INTO simulated_transactions VALUES (:transaction_id, :certificate_id, :project_id,
            :project_name, :credits, :price_per_tonne, :total_price, :offset_tonnes, :purchased_at)""", record)
    return record


def get_transactions(db_path: str | Path) -> list[dict]:
    with _connect(db_path) as conn:
        cursor = conn.execute("SELECT transaction_id, certificate_id, project_id, project_name, credits, price_per_tonne, total_price, offset_tonnes, purchased_at FROM simulated_transactions ORDER BY purchased_at DESC")
        keys = [column[0] for column in cursor.description]
        return [dict(zip(keys, row)) for row in cursor.fetchall()]
