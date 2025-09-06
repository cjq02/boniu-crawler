"""Database helper for MySQL connections and simple operations."""

import os
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

import pymysql


def get_db_config() -> Dict[str, Any]:
    """Load DB config from environment variables with sensible defaults."""
    return dict(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "fuye_user"),
        password=os.getenv("DB_PASSWORD", "fuye345abc"),
        database=os.getenv("DB_NAME", "im_fuye"),
        charset=os.getenv("DB_CHARSET", "utf8mb4"),
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )


def connect():
    """Create a new pymysql connection using env-based config."""
    return pymysql.connect(**get_db_config())


def fetch_all(sql: str, params: Optional[Sequence[Any]] = None) -> Iterable[Dict[str, Any]]:
    """Run a SELECT and yield rows as dicts."""
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            for row in cur.fetchall():
                yield row
    finally:
        conn.close()


def executemany(sql: str, rows: Sequence[Tuple[Any, ...]]) -> int:
    """Execute many rows; returns affected rows (approx)."""
    if not rows:
        return 0
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
            return cur.rowcount
    finally:
        conn.close()


