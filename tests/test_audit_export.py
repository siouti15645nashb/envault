"""Tests for audit log export feature."""
import json
import os
import pytest
from click.testing import CliRunner
from envault.audit import record_event
from envault.env_audit_export import (
    export_audit_log, export_audit_log_to_file,
    AuditExportError, SUPPORTED_FORMATS
)
from envault.cli_audit_export import audit_export_group


@pytest.fixture
def audit_dir(tmp_path):
    record_event(str(tmp_path), "set", key="FOO", details="value set")
    record_event(str(tmp_path), "get", key="BAR", details="value read")
    return str(tmp_path)


def test_supported_formats_constant():
    assert "json" in SUPPORTED_FORMATS
    assert "csv" in SUPPORTED_FORMATS
    assert "text" in SUPPORTED_FORMATS


def test_export_json_returns_valid_json(audit_dir):
    result = export_audit_log(audit_dir, "json")
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 2


def test_export_csv_contains_header(audit_dir):
    result = export_audit_log(audit_dir, "csv")
    assert "timestamp" in result
    assert "action" in result
    assert "FOO" in result


def test_export_text_contains_action(audit_dir):
    result = export_audit_log(audit_dir, "text")
    assert "set" in result
    assert "FOO" in result


def test_export_invalid_format_raises(audit_dir):
    with pytest.raises(AuditExportError):
        export_audit_log(audit_dir, "xml")


def test_export_empty_vault_returns_empty_list(tmp_path):
    result = export_audit_log(str(tmp_path), "json")
    assert json.loads(result) == []


def test_export_to_file(audit_dir, tmp_path):
    out = str(tmp_path / "audit_out.json")
    count = export_audit_log_to_file(audit_dir, out, "json")
    assert count == 2
    assert os.path.exists(out)
    with open(out) as f:
        data = json.load(f)
    assert len(data) == 2


def test_cli_export_run_stdout(audit_dir):
    runner = CliRunner()
    result = runner.invoke(audit_export_group, ["run", audit_dir, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 2


def test_cli_export_run_to_file(audit_dir, tmp_path):
    runner = CliRunner()
    out = str(tmp_path / "out.csv")
    result = runner.invoke(audit_export_group, ["run", audit_dir, "--format", "csv", "--output", out])
    assert result.exit_code == 0
    assert "Exported 2 entries" in result.output


def test_cli_formats_lists_all():
    runner = CliRunner()
    result = runner.invoke(audit_export_group, ["formats"])
    assert result.exit_code == 0
    for fmt in SUPPORTED_FORMATS:
        assert fmt in result.output
