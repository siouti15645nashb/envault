"""Tests for envault/import_env.py and envault/cli_import.py."""

import json
import os
import pytest
from click.testing import CliRunner

from envault.vault import init_vault, get_variable, list_variables
from envault.import_env import parse_dotenv, import_from_dotenv, ImportError as EnvImportError
from envault.cli_import import import_group

PASSWORD = "testpass"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, PASSWORD)
    return path


@pytest.fixture
def dotenv_file(tmp_path):
    path = tmp_path / ".env"
    path.write_text("API_KEY=abc123\nDB_URL=postgres://localhost/db\nDEBUG=true\n")
    return str(path)


@pytest.fixture
def runner():
    return CliRunner()


# --- parse_dotenv tests ---

def test_parse_dotenv_basic(dotenv_file):
    result = parse_dotenv(dotenv_file)
    assert result["API_KEY"] == "abc123"
    assert result["DB_URL"] == "postgres://localhost/db"
    assert result["DEBUG"] == "true"


def test_parse_dotenv_ignores_comments_and_blanks(tmp_path):
    f = tmp_path / ".env"
    f.write_text("# comment\n\nKEY=value\n")
    result = parse_dotenv(str(f))
    assert result == {"KEY": "value"}


def test_parse_dotenv_strips_quotes(tmp_path):
    f = tmp_path / ".env"
    f.write_text('QUOTED="hello world"\nSINGLE=\'hi\'\n')
    result = parse_dotenv(str(f))
    assert result["QUOTED"] == "hello world"
    assert result["SINGLE"] == "hi"


def test_parse_dotenv_missing_file(tmp_path):
    with pytest.raises(EnvImportError, match="File not found"):
        parse_dotenv(str(tmp_path / "nonexistent.env"))


def test_parse_dotenv_invalid_line(tmp_path):
    f = tmp_path / ".env"
    f.write_text("BADLINE\n")
    with pytest.raises(EnvImportError, match="missing '='"):
        parse_dotenv(str(f))


# --- import_from_dotenv tests ---

def test_import_from_dotenv_success(vault_file, dotenv_file):
    imported, skipped = import_from_dotenv(vault_file, dotenv_file, PASSWORD)
    assert set(imported) == {"API_KEY", "DB_URL", "DEBUG"}
    assert skipped == []
    assert get_variable(vault_file, PASSWORD, "API_KEY") == "abc123"


def test_import_skips_existing_without_overwrite(vault_file, dotenv_file):
    import_from_dotenv(vault_file, dotenv_file, PASSWORD)
    imported, skipped = import_from_dotenv(vault_file, dotenv_file, PASSWORD)
    assert imported == []
    assert set(skipped) == {"API_KEY", "DB_URL", "DEBUG"}


def test_import_overwrites_when_flag_set(vault_file, dotenv_file):
    import_from_dotenv(vault_file, dotenv_file, PASSWORD)
    imported, skipped = import_from_dotenv(vault_file, dotenv_file, PASSWORD, overwrite=True)
    assert set(imported) == {"API_KEY", "DB_URL", "DEBUG"}
    assert skipped == []


# --- CLI tests ---

def test_cli_import_dotenv_success(runner, vault_file, dotenv_file):
    result = runner.invoke(
        import_group,
        ["dotenv", dotenv_file, "--vault", vault_file, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Imported 3 variable(s)" in result.output


def test_cli_import_dotenv_skips_existing(runner, vault_file, dotenv_file):
    runner.invoke(import_group, ["dotenv", dotenv_file, "--vault", vault_file, "--password", PASSWORD])
    result = runner.invoke(
        import_group,
        ["dotenv", dotenv_file, "--vault", vault_file, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Skipped" in result.output


def test_cli_import_dotenv_missing_file(runner, vault_file, tmp_path):
    result = runner.invoke(
        import_group,
        ["dotenv", str(tmp_path / "missing.env"), "--vault", vault_file, "--password", PASSWORD],
    )
    assert result.exit_code == 1
    assert "Import error" in result.output
