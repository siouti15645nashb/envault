"""Tests for envault.history and envault.cli_history."""

import os
import json
import pytest
from click.testing import CliRunner
from envault.history import (
    record_change,
    get_history,
    clear_history,
    HistoryError,
    HISTORY_FILENAME,
    MAX_HISTORY_ENTRIES,
    _history_path,
)
from envault.cli_history import history_group


@pytest.fixture
def history_dir(tmp_path):
    return str(tmp_path)


def test_history_path_returns_correct_path(history_dir):
    path = _history_path(history_dir)
    assert path == os.path.join(history_dir, HISTORY_FILENAME)


def test_get_history_empty_when_no_file(history_dir):
    assert get_history(history_dir) == []


def test_record_change_creates_history_file(history_dir):
    record_change(history_dir, "MY_KEY", "set")
    assert os.path.exists(_history_path(history_dir))


def test_record_change_stores_correct_fields(history_dir):
    record_change(history_dir, "DB_URL", "set", actor="alice")
    entries = get_history(history_dir)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["key"] == "DB_URL"
    assert entry["action"] == "set"
    assert entry["actor"] == "alice"
    assert "timestamp" in entry


def test_record_change_invalid_action_raises(history_dir):
    with pytest.raises(HistoryError):
        record_change(history_dir, "KEY", "update")


def test_get_history_filtered_by_key(history_dir):
    record_change(history_dir, "KEY_A", "set", actor="alice")
    record_change(history_dir, "KEY_B", "set", actor="bob")
    record_change(history_dir, "KEY_A", "delete", actor="alice")
    result = get_history(history_dir, key="KEY_A")
    assert len(result) == 2
    assert all(e["key"] == "KEY_A" for e in result)


def test_clear_history_returns_count(history_dir):
    record_change(history_dir, "A", "set")
    record_change(history_dir, "B", "set")
    count = clear_history(history_dir)
    assert count == 2
    assert get_history(history_dir) == []


def test_history_trimmed_to_max_entries(history_dir):
    for i in range(MAX_HISTORY_ENTRIES + 10):
        record_change(history_dir, f"KEY_{i}", "set")
    with open(_history_path(history_dir)) as f:
        data = json.load(f)
    assert len(data) == MAX_HISTORY_ENTRIES


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_history_log_empty(runner, history_dir):
    vault_path = os.path.join(history_dir, ".envault")
    result = runner.invoke(history_group, ["log", "--vault", vault_path])
    assert result.exit_code == 0
    assert "No history" in result.output


def test_cli_history_log_shows_entries(runner, history_dir):
    record_change(history_dir, "SECRET", "set", actor="dev")
    vault_path = os.path.join(history_dir, ".envault")
    result = runner.invoke(history_group, ["log", "--vault", vault_path])
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "set" in result.output


def test_cli_history_clear(runner, history_dir):
    record_change(history_dir, "KEY", "set")
    vault_path = os.path.join(history_dir, ".envault")
    result = runner.invoke(history_group, ["clear", "--vault", vault_path], input="y\n")
    assert result.exit_code == 0
    assert "Cleared 1" in result.output
