"""Code snippet library MCP server with SQLite FTS5 and variable placeholders."""
from __future__ import annotations

from fastmcp import FastMCP

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
    raise NotImplementedError


@mcp.tool()
def search_snippets(query: str, language: str = "", limit: int = 20) -> dict[str, object]:
    """Search snippets by keyword using SQLite FTS5.

    Args:
        query: Full-text search query.
        language: Optional language filter.
        limit: Maximum number of results.

    Returns:
        A dict with key ``snippets`` containing a list of matching records.
    """
    raise NotImplementedError


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
        A dict with keys ``id``, ``title``, ``language``, and ``code``.
    """
    raise NotImplementedError


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
        limit: Maximum number of results.

    Returns:
        A dict with key ``snippets`` containing a list of snippet summaries.
    """
    raise NotImplementedError


@mcp.tool()
def delete_snippet(snippet_id: int) -> dict[str, object]:
    """Remove a snippet from the library by ID.

    Args:
        snippet_id: Numeric ID of the snippet to delete.

    Returns:
        A dict with key ``deleted`` set to True on success.
    """
    raise NotImplementedError


@mcp.tool()
def export_snippets(path: str, format: str = "json") -> dict[str, object]:  # noqa: A002
    """Export all snippets to a file.

    Args:
        path: Destination file path.
        format: Output format — ``json`` or ``markdown``.

    Returns:
        A dict with keys ``path`` and ``count``.
    """
    raise NotImplementedError


def run() -> None:
    """Run the MCP server."""
    mcp.run()
