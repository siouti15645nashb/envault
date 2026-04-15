"""Tests for envault/audit.py"""

import json
import os
import pytest
from pathlib import Path

from envault.audit import (
    record_event,
    get_log,
    clear_log,
    AUDIT_LOG_FILENAME,
    _audit_path,
)


@pytest.fixture
def audit_dir(tmp_path):
    """Provide a temporary directory for audit log tests."""
    return str(tmp_path)


def test_audit_log_filename_constant():
    assert AUDIT_LOG_FILENAME == ".envault_audit.json"


def test_audit_path_returns_correct_path(audit_dir):
    path = _audit_path(audit_dir)
    assert path.name == AUDIT_LOG_FILENAME
    assert path.parent == Path(audit_dir)


def test_get_log_empty_when_no_file(audit_dir):
    entries = get_log(audit_dir)
    assert entries == []


def test_record_event_creates_log_file(audit_dir):
    record_event("init", vault_dir=audit_dir)
    assert (Path(audit_dir) / AUDIT_LOG_FILENAME).exists()


def test_record_event_returns_entry(audit_dir):
    entry = record_event("set", key="DB_URL", actor="alice", vault_dir=audit_dir)
    assert entry["action"] == "set"
    assert entry["key"] == "DB_URL"
    assert entry["actor"] == "alice"
    assert "timestamp" in entry


def test_record_event_appends_multiple(audit_dir):
    record_event("init", vault_dir=audit_dir)
    record_event("set", key="FOO", vault_dir=audit_dir)
    record_event("get", key="FOO", vault_dir=audit_dir)
    entries = get_log(audit_dir)
    assert len(entries) == 3
    assert entries[0]["action"] == "init"
    assert entries[1]["action"] == "set"
    assert entries[2]["action"] == "get"


def test_record_event_uses_env_user_as_default_actor(audit_dir, monkeypatch):
    monkeypatch.setenv("USER", "bob")
    entry = record_event("list", vault_dir=audit_dir)
    assert entry["actor"] == "bob"


def test_clear_log_removes_entries(audit_dir):
    record_event("init", vault_dir=audit_dir)
    record_event("set", key="X", vault_dir=audit_dir)
    clear_log(audit_dir)
    assert get_log(audit_dir) == []


def test_get_log_returns_valid_json_structure(audit_dir):
    record_event("set", key="SECRET", actor="carol", vault_dir=audit_dir)
    log_path = Path(audit_dir) / AUDIT_LOG_FILENAME
    with open(log_path) as f:
        raw = json.load(f)
    assert isinstance(raw, list)
    assert raw[0]["key"] == "SECRET"
