import pytest
import json
from pathlib import Path
from envault.env_compliance import (
    COMPLIANCE_FILENAME,
    VALID_STANDARDS,
    ComplianceError,
    _compliance_path,
    set_compliance,
    remove_compliance,
    get_compliance,
    list_compliance,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    return path


def test_compliance_filename_constant():
    assert COMPLIANCE_FILENAME == ".envault_compliance.json"


def test_valid_standards_includes_common():
    for s in ["gdpr", "hipaa", "pci"]:
        assert s in VALID_STANDARDS


def test_compliance_path_returns_correct_path(vault_file):
    p = _compliance_path(vault_file)
    assert p.name == COMPLIANCE_FILENAME


def test_list_compliance_empty_when_no_file(vault_file):
    result = list_compliance(vault_file)
    assert result == {}


def test_set_compliance_creates_file(vault_file):
    set_compliance(vault_file, "API_KEY", "gdpr")
    p = _compliance_path(vault_file)
    assert p.exists()


def test_set_compliance_stores_standard(vault_file):
    set_compliance(vault_file, "API_KEY", "hipaa", note="PHI data")
    result = get_compliance(vault_file, "API_KEY")
    assert result["standard"] == "hipaa"
    assert result["note"] == "PHI data"


def test_set_compliance_invalid_standard_raises(vault_file):
    with pytest.raises(ComplianceError, match="Unknown standard"):
        set_compliance(vault_file, "API_KEY", "unknown_std")


def test_get_compliance_none_when_not_set(vault_file):
    assert get_compliance(vault_file, "MISSING_KEY") is None


def test_remove_compliance_success(vault_file):
    set_compliance(vault_file, "DB_PASS", "pci")
    remove_compliance(vault_file, "DB_PASS")
    assert get_compliance(vault_file, "DB_PASS") is None


def test_remove_compliance_missing_key_raises(vault_file):
    with pytest.raises(ComplianceError):
        remove_compliance(vault_file, "NONEXISTENT")


def test_list_compliance_returns_all(vault_file):
    set_compliance(vault_file, "KEY_A", "gdpr")
    set_compliance(vault_file, "KEY_B", "sox", note="audit")
    result = list_compliance(vault_file)
    assert "KEY_A" in result
    assert "KEY_B" in result
    assert result["KEY_B"]["note"] == "audit"
