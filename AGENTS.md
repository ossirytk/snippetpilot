# AGENTS.md — Project Rules for AI Assistants (Python)

snippetpilot is a code snippet library MCP server backed by a local SQLite database with FTS5 full-text search. Snippets support `{{placeholder}}` variable substitution and can be tagged, filtered by language, and exported to JSON or Markdown.

---

## Tech Stack

- **Language:** Python 3.12+
- **MCP Framework:** FastMCP
- **Storage:** SQLite with FTS5
- **Build / env:** uv + hatchling
- **Linter / formatter:** ruff
- **Tests:** pytest + pytest-cov

---

## Development Commands

```sh
# Install all dependencies (including dev)
uv sync

# Run the server
uv run snippetpilot

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Fix auto-fixable lint issues
uv run ruff check --fix .

# Run tests
uv run pytest
```

---

## Project Structure

```
snippetpilot/
├── src/
│   └── snippetpilot/
│       ├── __init__.py      # Package marker
│       ├── __main__.py      # python -m snippetpilot entry point
│       └── server.py        # FastMCP server + all tool definitions
├── pyproject.toml           # Project metadata, deps, ruff config
├── .python-version          # Pinned Python version (3.12)
├── AGENTS.md                # This file
└── README.md                # User-facing documentation
```

---

## Key Conventions

- All tool logic lives in `src/snippetpilot/server.py` initially; extract DB helpers into a sibling `db.py` module.
- Add dependencies with `uv add <package>`; add dev dependencies with `uv add --dev <package>`.
- ruff is the sole formatter and linter — never use black, isort, or other tools.
- `pyproject.toml` is the single source of truth for all ruff settings.
- Run `uv run ruff check --fix . && uv run ruff format .` before every commit.
