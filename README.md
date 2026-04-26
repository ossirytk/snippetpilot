# snippetpilot

Code snippet library MCP server with SQLite FTS5 search and `{{placeholder}}` variable expansion.

> **Status:** 🚧 Work in progress

snippetpilot stores reusable code snippets locally in a SQLite database. Snippets support full-text search, language and tag filtering, and `{{variable}}` substitution for template-style reuse.

---

## Tools

| Tool | Description |
|------|-------------|
| `save_snippet` | Save a new snippet with title, language, tags, and optional description |
| `search_snippets` | Full-text search across snippet titles, code, and descriptions |
| `expand_snippet` | Retrieve a snippet and substitute `{{placeholder}}` variables |
| `list_snippets` | Browse all snippets with optional language or tag filters |
| `delete_snippet` | Remove a snippet by ID |
| `export_snippets` | Export all snippets to a JSON or Markdown file |

---

## Installation

> Coming soon.

---

## Development

```sh
# Install dependencies
uv sync

# Run the server
uv run snippetpilot

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Run tests
uv run pytest
```
