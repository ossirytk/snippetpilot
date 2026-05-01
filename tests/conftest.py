"""Shared test fixtures for snippetpilot."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point SNIPPETPILOT_DB at a fresh temp database for each test."""
    db_file = tmp_path / "test_snippets.db"
    monkeypatch.setenv("SNIPPETPILOT_DB", str(db_file))
