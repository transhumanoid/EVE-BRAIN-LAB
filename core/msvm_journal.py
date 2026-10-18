"""MSVM journal: a minimal SQLite-backed journal for Eve Brain Lab.

The database path comes from the EVE_JOURNAL_DB environment variable,
defaulting to ./journals/msvm_journal.db.
"""
import argparse
import json
import os
import sqlite3
from datetime import datetime, timezone

DEFAULT_DB = os.path.join("journals", "msvm_journal.db")
SCHEMA_VERSION = "1"

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    topic     TEXT NOT NULL,
    content   TEXT NOT NULL,
    tags      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON entries(timestamp);
CREATE TABLE IF NOT EXISTS metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db_path():
    return os.environ.get("EVE_JOURNAL_DB") or DEFAULT_DB


def connect(path=None):
    path = path or db_path()
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path=None):
    """Create tables if missing. Safe to call repeatedly; never drops data."""
    with connect(path) as conn:
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT OR IGNORE INTO metadata(key, value) VALUES ('schema_version', ?)",
            (SCHEMA_VERSION,),
        )
        conn.execute(
            "INSERT OR IGNORE INTO metadata(key, value) VALUES ('created_at', ?)",
            (now_iso(),),
        )
    return path or db_path()


def schema_ok(path=None):
    path = path or db_path()
    if not os.path.exists(path):
        return False
    try:
        with sqlite3.connect(path) as conn:
            names = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
        return {"entries", "metadata"} <= names
    except sqlite3.DatabaseError:
        return False


def add_entry(topic, content, tags=(), timestamp=None, path=None):
    init_db(path)
    with connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO entries(timestamp, topic, content, tags) VALUES (?, ?, ?, ?)",
            (timestamp or now_iso(), topic, content, ",".join(tags)),
        )
        return cur.lastrowid


def get_entries(limit=20, topic=None, path=None):
    init_db(path)
    with connect(path) as conn:
        if topic:
            rows = conn.execute(
                "SELECT * FROM entries WHERE topic = ? ORDER BY id DESC LIMIT ?",
                (topic, limit))
        else:
            rows = conn.execute(
                "SELECT * FROM entries ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]


def get_entry(entry_id, path=None):
    with connect(path) as conn:
        r = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return dict(r) if r else None


def set_meta(key, value, path=None):
    init_db(path)
    with connect(path) as conn:
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value)),
        )


def get_meta(key, path=None):
    init_db(path)
    with connect(path) as conn:
        r = conn.execute("SELECT value FROM metadata WHERE key = ?", (key,)).fetchone()
        return r[0] if r else None


def main():
    p = argparse.ArgumentParser(description="MSVM journal")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    a = sub.add_parser("add")
    a.add_argument("topic")
    a.add_argument("content")
    a.add_argument("--tags", default="")
    l = sub.add_parser("list")
    l.add_argument("--limit", type=int, default=20)
    l.add_argument("--topic")
    args = p.parse_args()

    if args.cmd == "init":
        print(f"initialized {init_db()}")
    elif args.cmd == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        print(f"added entry {add_entry(args.topic, args.content, tags)}")
    elif args.cmd == "list":
        print(json.dumps(get_entries(args.limit, args.topic), indent=2))


if __name__ == "__main__":
    main()
