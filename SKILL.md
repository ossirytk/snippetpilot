---
name: snippetpilot
description: Code snippet library with full-text search and template variable expansion. Use this skill when the user wants to save, find, or reuse code snippets. Invoke for prompts like "save this snippet", "find my boilerplate for X", "show me my SQL snippets", "expand the auth template", or "export my snippet library".
---

## Overview

snippetpilot stores reusable code snippets in a local SQLite database with FTS5 full-text search. Snippets support language and tag filtering, and `{{variable}}` substitution for template-style reuse.

## Available Tools

| Tool | When to use |
|------|-------------|
| `snippetpilot-save_snippet` | Save a new snippet. Required: `title`, `code`. Optional: `language`, `tags` (array), `description`. |
| `snippetpilot-search_snippets` | Full-text search across titles, code, and descriptions. Required: `query`. Optional: `language`, `tags`, `limit`. |
| `snippetpilot-expand_snippet` | Retrieve a snippet and substitute `{{placeholder}}` variables. Required: `id`. Optional: `vars` (dict of placeholder → value). |
| `snippetpilot-list_snippets` | Browse all snippets. Optional: `language`, `tags`, `limit`. |
| `snippetpilot-delete_snippet` | Remove a snippet by ID. Required: `id`. |
| `snippetpilot-export_snippets` | Export all snippets to a JSON or Markdown file. Required: `path`. Optional: `format` (`json`/`markdown`). |

## Guidance

- **Saving**: always set `language` and `tags` to make snippets easier to find later.
- **Searching**: use `search_snippets` for keyword-based discovery; narrow with `language` or `tags` if results are broad.
- **Templates**: when a snippet has `{{placeholders}}`, use `expand_snippet` with a `vars` dict to fill them in before using.
- **Reuse pattern**: `search_snippets` → `expand_snippet` → paste into code.
