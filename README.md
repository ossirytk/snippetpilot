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

**Requires:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

### Option A — Install as a uv tool (recommended)

```sh
uv tool install git+https://github.com/ossirytk/snippetpilot
```

Verify:

```sh
snippetpilot --help
```

To update later:

```sh
uv tool upgrade snippetpilot
```

### Option B — Clone and run from source

```sh
git clone https://github.com/ossirytk/snippetpilot
cd snippetpilot
uv sync
```

---

## Configuration

### GitHub Copilot CLI

Add to `~/.copilot/mcp-config.json`:

**Option A (installed tool):**

```json
{
  "mcpServers": {
    "snippetpilot": {
      "type": "stdio",
      "command": "snippetpilot"
    }
  }
}
```

**Option B (local clone):**

```json
{
  "mcpServers": {
    "snippetpilot": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/snippetpilot", "snippetpilot"]
    }
  }
}
```

### VS Code Copilot

Add to your user-level MCP config file:
- **Linux:** `~/.config/Code/User/mcp.json`
- **macOS:** `~/Library/Application Support/Code/User/mcp.json`
- **Windows:** `%APPDATA%\Code\User\mcp.json`

**Option A:**

```json
{
  "servers": {
    "snippetpilot": {
      "type": "stdio",
      "command": "snippetpilot"
    }
  }
}
```

**Option B:**

```json
{
  "servers": {
    "snippetpilot": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/snippetpilot", "snippetpilot"]
    }
  }
}
```

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
