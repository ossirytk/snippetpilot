"""Shared test fixtures for snippetpilot."""

from __future__ import annotations

import pytest


@pytest.fixture()
def db(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Point SNIPPETPILOT_DB at a fresh temp database for each test."""
    db_file = tmp_path / "test_snippets.db"
    monkeypatch.setenv("SNIPPETPILOT_DB", str(db_file))
