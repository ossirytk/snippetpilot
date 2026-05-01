"""Code snippet library MCP server with SQLite FTS5 and variable placeholders."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from fastmcp import FastMCP

from snippetpilot.db import get_connection, tags_csv_to_list

mcp: FastMCP = FastMCP(
    name="snippetpilot",
    instructions=(
        "snippetpilot is a personal code snippet library. "
        "Use `save_snippet` to store a reusable snippet with a title, language, and optional tags. "
        "Use `search_snippets` to find snippets by keyword using full-text search. "
        "Use `expand_snippet` to retrieve a snippet and fill in {{placeholder}} variables. "
        "Use `list_snippets` to browse all snippets with optional language or tag filters. "
        "Use `delete_snippet` to remove a snippet by ID. "
        "Use `export_snippets` to export all snippets to a JSON or Markdown file."
    ),
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_TAGS_SUBQUERY = "(SELECT GROUP_CONCAT(t.tag) FROM snippet_tags t WHERE t.snippet_id = s.id) AS tags"

_MAX_LIMIT = 200

_LIST_SQL = f"""
    SELECT s.id, s.title, s.language, s.description, s.created_at, {_TAGS_SUBQUERY}
    FROM snippets s
    WHERE (:language = '' OR s.language = :language)
      AND (:tag = '' OR EXISTS (
          SELECT 1 FROM snippet_tags st
          WHERE st.snippet_id = s.id AND st.tag = :tag
      ))
    ORDER BY s.created_at DESC
    LIMIT :limit
"""  # noqa: S608

_SEARCH_SQL = f"""
    SELECT s.id, s.title, s.language, s.description, s.created_at, {_TAGS_SUBQUERY}
    FROM snippets_fts fts
    JOIN snippets s ON s.id = fts.rowid
    WHERE snippets_fts MATCH :query
      AND (:language = '' OR s.language = :language)
    ORDER BY bm25(snippets_fts)
    LIMIT :limit
"""  # noqa: S608


def _normalize(value: str) -> str:
    return value.strip().lower()


def _row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "title": row["title"],
        "code": row["code"],
        "language": row["language"],
        "description": row["description"],
        "created_at": row["created_at"],
        "tags": tags_csv_to_list(row["tags"]),
    }


def _summary_row_to_dict(row: sqlite3.Row) -> dict[str, object]:
    return {
        "id": row["id"],
        "title": row["title"],
        "language": row["language"],
        "description": row["description"],
        "created_at": row["created_at"],
        "tags": tags_csv_to_list(row["tags"]),
    }


def _make_fence(code: str) -> str:
    """Return a backtick fence longer than any run in the code."""
    max_run = max((len(m.group(0)) for m in re.finditer(r"`+", code)), default=0)
    return "`" * max(3, max_run + 1)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def save_snippet(
    title: str,
    code: str,
    language: str = "",
    tags: list[str] | None = None,
    description: str = "",
) -> dict[str, object]:
    """Save a new code snippet to the library.

    Args:
        title: Short name for the snippet.
        code: The snippet body. Use ``{{var}}`` syntax for placeholders.
        language: Programming language identifier (e.g. ``python``, ``bash``).
        tags: Optional list of tag strings for filtering.
        description: Optional longer description.

    Returns:
        A dict with keys ``id`` and ``title``.
    """
    if not title.strip():
        msg = "title must not be empty"
        raise ValueError(msg)
    if not code:
        msg = "code must not be empty"
        raise ValueError(msg)

    raw_tags = [t for t in (tags or []) if t.strip()]
    for tag in raw_tags:
        if "," in tag:
            msg = f"tag must not contain a comma: {tag!r}"
            raise ValueError(msg)
    normalized_tags = sorted({_normalize(t) for t in raw_tags})
    lang = _normalize(language)

    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO snippets (title, code, language, description) VALUES (?, ?, ?, ?)",
            (title.strip(), code, lang, description.strip()),
        )
        snippet_id = cur.lastrowid
        if normalized_tags:
            conn.executemany(
                "INSERT OR IGNORE INTO snippet_tags (snippet_id, tag) VALUES (?, ?)",
                [(snippet_id, t) for t in normalized_tags],
            )
        conn.commit()

    return {"id": snippet_id, "title": title.strip()}


@mcp.tool()
def search_snippets(query: str, language: str = "", limit: int = 20) -> dict[str, object]:
    """Search snippets by keyword using SQLite FTS5.

    Args:
        query: Full-text search query (supports FTS5 syntax).
        language: Optional language filter.
        limit: Maximum number of results (1-200).

    Returns:
        A dict with key ``snippets`` containing a list of matching records.
    """
    if not query.strip():
        msg = "query must not be empty"
        raise ValueError(msg)
    if limit < 1 or limit > _MAX_LIMIT:
        msg = "limit must be between 1 and 200"
        raise ValueError(msg)

    with get_connection() as conn:
        try:
            rows = conn.execute(
                _SEARCH_SQL,
                {"query": query.strip(), "language": _normalize(language), "limit": limit},
            ).fetchall()
        except sqlite3.OperationalError as exc:
            msg = f"Invalid search query: {exc}"
            raise ValueError(msg) from exc

    return {"snippets": [_summary_row_to_dict(r) for r in rows]}


@mcp.tool()
def expand_snippet(
    snippet_id: int,
    variables: dict[str, str] | None = None,
) -> dict[str, object]:
    """Retrieve a snippet and substitute ``{{placeholder}}`` variables.

    Args:
        snippet_id: Numeric ID of the snippet.
        variables: Mapping of placeholder names to replacement values.

    Returns:
        A dict with keys ``id``, ``title``, ``language``, ``code``,
        and ``unresolved_variables`` (placeholders with no supplied value).
    """
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM snippets WHERE id = ?", (snippet_id,)).fetchone()

    if row is None:
        msg = f"Snippet {snippet_id} not found"
        raise ValueError(msg)

    vars_map = variables or {}
    code = re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: vars_map.get(m.group(1), m.group(0)),
        row["code"],
    )
    unresolved = re.findall(r"\{\{(\w+)\}\}", code)

    return {
        "id": row["id"],
        "title": row["title"],
        "language": row["language"],
        "code": code,
        "unresolved_variables": unresolved,
    }


@mcp.tool()
def list_snippets(
    language: str = "",
    tag: str = "",
    limit: int = 50,
) -> dict[str, object]:
    """Browse all snippets with optional filters.

    Args:
        language: Filter by language identifier.
        tag: Filter by tag name.
        limit: Maximum number of results (1-200).

    Returns:
        A dict with key ``snippets`` containing a list of snippet summaries.
    """
    if limit < 1 or limit > _MAX_LIMIT:
        msg = "limit must be between 1 and 200"
        raise ValueError(msg)

    with get_connection() as conn:
        rows = conn.execute(
            _LIST_SQL,
            {"language": _normalize(language), "tag": _normalize(tag), "limit": limit},
        ).fetchall()

    return {"snippets": [_summary_row_to_dict(r) for r in rows]}


@mcp.tool()
def delete_snippet(snippet_id: int) -> dict[str, object]:
    """Remove a snippet from the library by ID.

    Args:
        snippet_id: Numeric ID of the snippet to delete.

    Returns:
        A dict with key ``deleted`` set to True on success.
    """
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        conn.commit()

    if cur.rowcount == 0:
        msg = f"Snippet {snippet_id} not found"
        raise ValueError(msg)

    return {"deleted": True}


@mcp.tool()
def export_snippets(path: str, format: str = "json") -> dict[str, object]:  # noqa: A002
    """Export all snippets to a file.

    Args:
        path: Destination file path.
        format: Output format — ``json`` or ``markdown``.

    Returns:
        A dict with keys ``path`` and ``count``.
    """
    if format not in ("json", "markdown"):
        msg = "format must be 'json' or 'markdown'"
        raise ValueError(msg)

    export_path = Path(path).expanduser().resolve()
    export_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT s.id, s.title, s.code, s.language, s.description, s.created_at,
                   {_TAGS_SUBQUERY}
            FROM snippets s
            ORDER BY s.created_at
            """,  # noqa: S608
        ).fetchall()

    snippets = [_row_to_dict(r) for r in rows]

    if format == "json":
        export_path.write_text(json.dumps(snippets, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        _write_markdown(export_path, snippets)

    return {"path": str(export_path), "count": len(snippets)}


def _write_markdown(path: Path, snippets: list[dict[str, object]]) -> None:
    parts: list[str] = []
    for s in snippets:
        title = s["title"]
        lang = s["language"] or ""
        tags = s["tags"]
        desc = s["description"]
        code = str(s["code"])
        created = s["created_at"]

        meta_parts = []
        if lang:
            meta_parts.append(f"**Language:** {lang}")
        if tags:
            meta_parts.append(f"**Tags:** {', '.join(str(t) for t in tags)}")  # type: ignore[arg-type]
        meta_parts.append(f"**ID:** {s['id']} | **Created:** {created}")

        fence = _make_fence(code)
        block = [f"## {title}", "", "  ".join(meta_parts)]
        if desc:
            block += ["", str(desc)]
        block += ["", f"{fence}{lang}", code, fence, ""]
        parts.append("\n".join(block))

    path.write_text("\n---\n\n".join(parts), encoding="utf-8")


def run() -> None:
    """Run the MCP server."""
    mcp.run()
