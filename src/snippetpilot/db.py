"""SQLite database helpers for snippetpilot."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

_INIT_SQL = """\
CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS snippet_tags (
    snippet_id INTEGER NOT NULL REFERENCES snippets(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (snippet_id, tag)
);

CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5(
    title, code, description,
    content=snippets,
    content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS snippets_ai AFTER INSERT ON snippets BEGIN
    INSERT INTO snippets_fts(rowid, title, code, description)
    VALUES (new.id, new.title, new.code, new.description);
END;

CREATE TRIGGER IF NOT EXISTS snippets_ad AFTER DELETE ON snippets BEGIN
    INSERT INTO snippets_fts(snippets_fts, rowid, title, code, description)
    VALUES ('delete', old.id, old.title, old.code, old.description);
END;

CREATE TRIGGER IF NOT EXISTS snippets_au AFTER UPDATE ON snippets BEGIN
    INSERT INTO snippets_fts(snippets_fts, rowid, title, code, description)
    VALUES ('delete', old.id, old.title, old.code, old.description);
    INSERT INTO snippets_fts(rowid, title, code, description)
    VALUES (new.id, new.title, new.code, new.description);
END;
"""


def get_db_path() -> Path:
    """Return the path to the SQLite database file."""
    env = os.environ.get("SNIPPETPILOT_DB")
    if env:
        return Path(env)
    return Path.home() / ".local" / "share" / "snippetpilot" / "snippets.db"


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Yield a configured SQLite connection, initialising the schema on first use."""
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(_INIT_SQL)
    try:
        yield conn
    finally:
        conn.close()


def tags_csv_to_list(tags_csv: str | None) -> list[str]:
    """Split a comma-separated tag string into a clean list."""
    if not tags_csv:
        return []
    return [t for t in tags_csv.split(",") if t]
