"""Tests for snippetpilot MCP tools."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from snippetpilot.server import (
    delete_snippet,
    expand_snippet,
    export_snippets,
    list_snippets,
    save_snippet,
    search_snippets,
)

# ---------------------------------------------------------------------------
# save_snippet
# ---------------------------------------------------------------------------


def test_save_snippet_returns_id_and_title(db: None) -> None:
    result = save_snippet(title="Hello", code="print('hello')", language="python")
    assert result["id"] == 1
    assert result["title"] == "Hello"


def test_save_snippet_trims_title(db: None) -> None:
    result = save_snippet(title="  Trimmed  ", code="x = 1")
    assert result["title"] == "Trimmed"


def test_save_snippet_normalises_language_and_tags(db: None) -> None:
    save_snippet(title="S", code="x", language="Python", tags=["Alpha", "beta", " Alpha "])
    snippets = list_snippets()["snippets"]
    assert snippets[0]["language"] == "python"
    assert sorted(snippets[0]["tags"]) == ["alpha", "beta"]


def test_save_snippet_empty_title_raises(db: None) -> None:
    with pytest.raises(ValueError, match="title"):
        save_snippet(title="   ", code="x = 1")


def test_save_snippet_empty_code_raises(db: None) -> None:
    with pytest.raises(ValueError, match="code"):
        save_snippet(title="T", code="")


def test_save_snippet_tag_with_comma_raises(db: None) -> None:
    with pytest.raises(ValueError, match="comma"):
        save_snippet(title="T", code="x", tags=["foo,bar"])


def test_save_snippet_no_tags(db: None) -> None:
    result = save_snippet(title="NoTags", code="pass")
    assert result["id"] is not None
    snippets = list_snippets()["snippets"]
    assert snippets[0]["tags"] == []


# ---------------------------------------------------------------------------
# list_snippets
# ---------------------------------------------------------------------------


def test_list_snippets_empty(db: None) -> None:
    assert list_snippets()["snippets"] == []


def test_list_snippets_returns_all(db: None) -> None:
    save_snippet(title="A", code="a", language="python")
    save_snippet(title="B", code="b", language="bash")
    result = list_snippets()
    assert len(result["snippets"]) == 2


def test_list_snippets_language_filter(db: None) -> None:
    save_snippet(title="A", code="a", language="python")
    save_snippet(title="B", code="b", language="bash")
    result = list_snippets(language="python")
    assert len(result["snippets"]) == 1
    assert result["snippets"][0]["title"] == "A"


def test_list_snippets_tag_filter(db: None) -> None:
    save_snippet(title="A", code="a", tags=["web", "api"])
    save_snippet(title="B", code="b", tags=["cli"])
    result = list_snippets(tag="api")
    assert len(result["snippets"]) == 1
    assert result["snippets"][0]["title"] == "A"


def test_list_snippets_language_and_tag_filter(db: None) -> None:
    save_snippet(title="A", code="a", language="python", tags=["web"])
    save_snippet(title="B", code="b", language="python", tags=["cli"])
    save_snippet(title="C", code="c", language="bash", tags=["web"])
    result = list_snippets(language="python", tag="web")
    assert len(result["snippets"]) == 1
    assert result["snippets"][0]["title"] == "A"


def test_list_snippets_invalid_limit_raises(db: None) -> None:
    with pytest.raises(ValueError, match="limit"):
        list_snippets(limit=0)


def test_list_snippets_tag_filter_returns_all_snippet_tags(db: None) -> None:
    """Tag filter should not drop the other tags from the returned snippet."""
    save_snippet(title="A", code="a", tags=["alpha", "beta"])
    result = list_snippets(tag="alpha")
    assert sorted(result["snippets"][0]["tags"]) == ["alpha", "beta"]


# ---------------------------------------------------------------------------
# search_snippets
# ---------------------------------------------------------------------------


def test_search_snippets_finds_by_title(db: None) -> None:
    save_snippet(title="quicksort algorithm", code="def qs(): ...")
    result = search_snippets(query="quicksort")
    assert len(result["snippets"]) == 1
    assert result["snippets"][0]["title"] == "quicksort algorithm"


def test_search_snippets_finds_by_code(db: None) -> None:
    save_snippet(title="Hello", code="print('hello world')")
    result = search_snippets(query="hello world")
    assert len(result["snippets"]) == 1


def test_search_snippets_empty_query_raises(db: None) -> None:
    with pytest.raises(ValueError, match="query"):
        search_snippets(query="")


def test_search_snippets_language_filter(db: None) -> None:
    save_snippet(title="py sort", code="list.sort()", language="python")
    save_snippet(title="rb sort", code="array.sort", language="ruby")
    result = search_snippets(query="sort", language="python")
    assert len(result["snippets"]) == 1
    assert result["snippets"][0]["language"] == "python"


def test_search_snippets_no_results(db: None) -> None:
    save_snippet(title="Hello", code="print('hello')")
    result = search_snippets(query="nonexistent_xyz")
    assert result["snippets"] == []


def test_search_snippets_invalid_query_raises(db: None) -> None:
    with pytest.raises(ValueError, match="Invalid search query"):
        search_snippets(query='"unclosed')


def test_search_snippets_invalid_limit_raises(db: None) -> None:
    with pytest.raises(ValueError, match="limit"):
        search_snippets(query="x", limit=0)


# ---------------------------------------------------------------------------
# expand_snippet
# ---------------------------------------------------------------------------


def test_expand_snippet_substitutes_variables(db: None) -> None:
    save_snippet(title="Greet", code="Hello, {{name}}!")
    result = expand_snippet(snippet_id=1, variables={"name": "world"})
    assert result["code"] == "Hello, world!"
    assert result["unresolved_variables"] == []


def test_expand_snippet_reports_unresolved(db: None) -> None:
    save_snippet(title="T", code="{{a}} and {{b}}")
    result = expand_snippet(snippet_id=1, variables={"a": "one"})
    assert "one" in result["code"]
    assert "{{b}}" in result["code"]
    assert result["unresolved_variables"] == ["b"]


def test_expand_snippet_no_variables(db: None) -> None:
    save_snippet(title="Plain", code="no placeholders here")
    result = expand_snippet(snippet_id=1)
    assert result["code"] == "no placeholders here"
    assert result["unresolved_variables"] == []


def test_expand_snippet_extra_variables_ignored(db: None) -> None:
    save_snippet(title="T", code="Hello, {{name}}!")
    result = expand_snippet(snippet_id=1, variables={"name": "Alice", "extra": "ignored"})
    assert result["code"] == "Hello, Alice!"


def test_expand_snippet_not_found_raises(db: None) -> None:
    with pytest.raises(ValueError, match="not found"):
        expand_snippet(snippet_id=999)


# ---------------------------------------------------------------------------
# delete_snippet
# ---------------------------------------------------------------------------


def test_delete_snippet_removes_it(db: None) -> None:
    save_snippet(title="ToDel", code="x")
    result = delete_snippet(snippet_id=1)
    assert result["deleted"] is True
    assert list_snippets()["snippets"] == []


def test_delete_snippet_cascades_tags(db: None) -> None:
    save_snippet(title="T", code="x", tags=["a", "b"])
    delete_snippet(snippet_id=1)
    # Re-save and list to confirm fresh state
    save_snippet(title="New", code="y", tags=["c"])
    result = list_snippets()
    assert len(result["snippets"]) == 1
    assert result["snippets"][0]["tags"] == ["c"]


def test_delete_snippet_not_found_raises(db: None) -> None:
    with pytest.raises(ValueError, match="not found"):
        delete_snippet(snippet_id=42)


def test_delete_removes_from_search_index(db: None) -> None:
    save_snippet(title="findme unique_token", code="x")
    delete_snippet(snippet_id=1)
    result = search_snippets(query="unique_token")
    assert result["snippets"] == []


# ---------------------------------------------------------------------------
# export_snippets
# ---------------------------------------------------------------------------


def test_export_json(db: None, tmp_path: Path) -> None:
    save_snippet(title="A", code="a = 1", language="python", tags=["math"])
    save_snippet(title="B", code="b = 2")
    out = tmp_path / "out.json"
    result = export_snippets(path=str(out), format="json")
    assert result["count"] == 2
    data = json.loads(out.read_text())
    assert len(data) == 2
    assert data[0]["title"] == "A"
    assert data[0]["language"] == "python"
    assert data[0]["tags"] == ["math"]


def test_export_markdown(db: None, tmp_path: Path) -> None:
    save_snippet(title="Snippet", code="print('hi')", language="python")
    out = tmp_path / "out.md"
    result = export_snippets(path=str(out), format="markdown")
    assert result["count"] == 1
    content = out.read_text()
    assert "## Snippet" in content
    assert "print('hi')" in content
    assert "```python" in content


def test_export_markdown_handles_backticks(db: None, tmp_path: Path) -> None:
    save_snippet(title="T", code="before\n```nested```\nafter")
    out = tmp_path / "bt.md"
    export_snippets(path=str(out), format="markdown")
    content = out.read_text()
    # Fence must be longer than the nested triple-backtick run
    assert "````" in content


def test_export_invalid_format_raises(db: None, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="format"):
        export_snippets(path=str(tmp_path / "out.txt"), format="xml")


def test_export_empty_library(db: None, tmp_path: Path) -> None:
    out = tmp_path / "empty.json"
    result = export_snippets(path=str(out), format="json")
    assert result["count"] == 0
    assert json.loads(out.read_text()) == []
