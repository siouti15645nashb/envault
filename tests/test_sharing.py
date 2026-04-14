"""Tests for envault.sharing — team bundle export/import."""

import json
import base64
import pytest
from pathlib import Path

from envault.vault import init_vault, set_variable, get_variable
from envault.sharing import export_bundle, import_bundle, BUNDLE_VERSION


PASSPHRASE = "shared-team-secret"


@pytest.fixture
def vault_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    vault = tmp_path / ".envault"
    init_vault(vault, PASSPHRASE)
    return vault


@pytest.fixture
def populated_vault(vault_file):
    set_variable(vault_file, PASSPHRASE, "API_KEY", "abc123")
    set_variable(vault_file, PASSPHRASE, "DB_URL", "postgres://localhost/db")
    return vault_file


def test_export_bundle_returns_string(populated_vault):
    bundle = export_bundle(PASSPHRASE, populated_vault)
    assert isinstance(bundle, str)
    assert len(bundle) > 0


def test_export_bundle_is_base64_encoded(populated_vault):
    bundle = export_bundle(PASSPHRASE, populated_vault)
    decoded = base64.b64decode(bundle.encode()).decode()
    parsed = json.loads(decoded)
    assert "version" in parsed
    assert "salt" in parsed
    assert "variables" in parsed


def test_export_bundle_has_correct_version(populated_vault):
    bundle = export_bundle(PASSPHRASE, populated_vault)
    decoded = json.loads(base64.b64decode(bundle.encode()).decode())
    assert decoded["version"] == BUNDLE_VERSION


def test_export_bundle_contains_all_variables(populated_vault):
    bundle = export_bundle(PASSPHRASE, populated_vault)
    decoded = json.loads(base64.b64decode(bundle.encode()).decode())
    assert "API_KEY" in decoded["variables"]
    assert "DB_URL" in decoded["variables"]


def test_import_bundle_restores_variables(tmp_path, monkeypatch):
    """Export from one vault, import into a fresh vault."""
    # Source vault
    src = tmp_path / "src" / ".envault"
    src.parent.mkdir()
    init_vault(src, PASSPHRASE)
    set_variable(src, PASSPHRASE, "SECRET", "hunter2")

    bundle = export_bundle(PASSPHRASE, src)

    # Destination vault
    dst = tmp_path / "dst" / ".envault"
    dst.parent.mkdir()
    init_vault(dst, PASSPHRASE)

    imported = import_bundle(bundle, PASSPHRASE, dst)

    assert "SECRET" in imported
    assert get_variable(dst, PASSPHRASE, "SECRET") == "hunter2"


def test_import_bundle_returns_list_of_names(populated_vault, tmp_path):
    bundle = export_bundle(PASSPHRASE, populated_vault)

    dst = tmp_path / "dst" / ".envault"
    dst.parent.mkdir()
    init_vault(dst, PASSPHRASE)

    imported = import_bundle(bundle, PASSPHRASE, dst)
    assert set(imported) == {"API_KEY", "DB_URL"}


def test_import_bundle_raises_on_invalid_base64(vault_file):
    with pytest.raises(ValueError, match="Invalid bundle format"):
        import_bundle("not-valid-base64!!!", PASSPHRASE, vault_file)


def test_import_bundle_raises_on_wrong_version(vault_file):
    bad_bundle = base64.b64encode(
        json.dumps({"version": 99, "salt": "aa", "variables": {}}).encode()
    ).decode()
    with pytest.raises(ValueError, match="Unsupported bundle version"):
        import_bundle(bad_bundle, PASSPHRASE, vault_file)


def test_export_empty_vault(vault_file):
    bundle = export_bundle(PASSPHRASE, vault_file)
    decoded = json.loads(base64.b64decode(bundle.encode()).decode())
    assert decoded["variables"] == {}
