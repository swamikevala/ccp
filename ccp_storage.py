import os
import sqlite3
from datetime import datetime
from typing import Iterable, Optional, Dict, Any, List


DEFAULT_DB_PATH = os.environ.get("CCP_DB_PATH", "ccp.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL,
    topic TEXT NOT NULL,
    headline TEXT NOT NULL,
    source TEXT NOT NULL,
    published_date TEXT,
    summary TEXT,
    url TEXT,
    tone REAL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_items_created_at ON items (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_items_type ON items (item_type);
"""


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    return sqlite3.connect(db_path or DEFAULT_DB_PATH)


def init_db(db_path: Optional[str] = None) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)


def save_items(items: Iterable[Dict[str, Any]], db_path: Optional[str] = None) -> int:
    inserted = 0
    with get_connection(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        for item in items:
            values = (
                item["id"],
                item["item_type"],
                item["topic"],
                item["headline"],
                item["source"],
                item.get("published_date"),
                item.get("summary"),
                item.get("url"),
                item.get("tone"),
                item.get("created_at") or datetime.utcnow().isoformat(),
            )
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO items
                (id, item_type, topic, headline, source, published_date, summary, url, tone, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            if cursor.rowcount == 1:
                inserted += 1
    return inserted


def list_items(
    db_path: Optional[str] = None,
    limit: int = 100,
    item_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = """
        SELECT id, item_type, topic, headline, source, published_date, summary, url, tone, created_at
        FROM items
    """
    params = []
    if item_type:
        query += " WHERE item_type = ?"
        params.append(item_type)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_connection(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
