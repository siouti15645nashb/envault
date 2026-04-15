"""Tests for the audit CLI commands (audit log and audit clear)."""

import json
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envault.cli_audit import audit_group, cmd_audit_log, cmd_audit_clear
from envault.audit import record_event, get_log, _audit_path


@pytest.fixture
def runner():
    """Provide a Click test runner."""
    return CliRunner()


@pytest.fixture
def audit_dir(tmp_path, monkeypatch):
    """Redirect audit log to a temporary directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def populated_audit(audit_dir):
    """Create an audit log with a few sample events."""
    record_event("init", details="vault initialised")
    record_event("set", variable="API_KEY", details="variable set")
    record_event("get", variable="API_KEY", details="variable retrieved")
    return audit_dir


# ---------------------------------------------------------------------------
# cmd_audit_log
# ---------------------------------------------------------------------------

class TestCmdAuditLog:
    def test_audit_log_empty(self, runner, audit_dir):
        """Should report no events when the log file does not exist."""
        result = runner.invoke(audit_group, ["log"])
        assert result.exit_code == 0
        assert "No audit events" in result.output or "empty" in result.output.lower()

    def test_audit_log_shows_events(self, runner, populated_audit):
        """Should display recorded events."""
        result = runner.invoke(audit_group, ["log"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "set" in result.output
        assert "get" in result.output

    def test_audit_log_shows_variable_name(self, runner, populated_audit):
        """Variable names should appear in the log output."""
        result = runner.invoke(audit_group, ["log"])
        assert result.exit_code == 0
        assert "API_KEY" in result.output

    def test_audit_log_shows_timestamps(self, runner, populated_audit):
        """Each event entry should include a timestamp."""
        result = runner.invoke(audit_group, ["log"])
        assert result.exit_code == 0
        # ISO-8601 timestamps contain 'T' separator
        assert "T" in result.output or "-" in result.output

    def test_audit_log_json_flag(self, runner, populated_audit):
        """--json flag should emit valid JSON output."""
        result = runner.invoke(audit_group, ["log", "--json"])
        assert result.exit_code == 0
        parsed = json.loads(result.output)
        assert isinstance(parsed, list)
        assert len(parsed) == 3


# ---------------------------------------------------------------------------
# cmd_audit_clear
# ---------------------------------------------------------------------------

class TestCmdAuditClear:
    def test_audit_clear_removes_log(self, runner, populated_audit):
        """After clearing, the log file should no longer exist."""
        log_path = _audit_path(populated_audit)
        assert log_path.exists()
        result = runner.invoke(audit_group, ["clear"], input="y\n")
        assert result.exit_code == 0
        assert not log_path.exists()

    def test_audit_clear_confirms_action(self, runner, populated_audit):
        """Output should confirm that the log was cleared."""
        result = runner.invoke(audit_group, ["clear"], input="y\n")
        assert result.exit_code == 0
        assert "cleared" in result.output.lower() or "removed" in result.output.lower()

    def test_audit_clear_aborts_on_no(self, runner, populated_audit):
        """Answering 'n' should abort without deleting the log."""
        log_path = _audit_path(populated_audit)
        result = runner.invoke(audit_group, ["clear"], input="n\n")
        assert result.exit_code == 0 or result.exit_code == 1
        assert log_path.exists()

    def test_audit_clear_no_file_is_graceful(self, runner, audit_dir):
        """Clearing when no log exists should not raise an error."""
        result = runner.invoke(audit_group, ["clear"], input="y\n")
        assert result.exit_code == 0
