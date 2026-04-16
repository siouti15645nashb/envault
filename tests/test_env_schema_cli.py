import pytest
import os
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.env_schema_cli import schema_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    set_variable(path, "secret", "DB_URL", "postgres://localhost/db")
    set_variable(path, "secret", "API_KEY", "abc123")
    return path


def test_schema_define_success(runner, vault_file):
    result = runner.invoke(schema_group, ["define", "DB_URL", vault_file])
    assert result.exit_code == 0
    assert "defined" in result.output


def test_schema_define_with_options(runner, vault_file):
    result = runner.invoke(schema_group, [
        "define", "API_KEY", "--pattern", r"^[a-z0-9]+$",
        "--description", "API key", vault_file
    ])
    assert result.exit_code == 0
    assert "defined" in result.output


def test_schema_list_empty(runner, vault_file):
    result = runner.invoke(schema_group, ["list", vault_file])
    assert result.exit_code == 0
    assert "No schema fields" in result.output


def test_schema_list_shows_fields(runner, vault_file):
    runner.invoke(schema_group, ["define", "DB_URL", vault_file])
    runner.invoke(schema_group, ["define", "API_KEY", "--optional", vault_file])
    result = runner.invoke(schema_group, ["list", vault_file])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "API_KEY" in result.output
    assert "optional" in result.output


def test_schema_remove_success(runner, vault_file):
    runner.invoke(schema_group, ["define", "DB_URL", vault_file])
    result = runner.invoke(schema_group, ["remove", "DB_URL", vault_file])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_schema_remove_nonexistent(runner, vault_file):
    result = runner.invoke(schema_group, ["remove", "NONEXISTENT", vault_file])
    assert result.exit_code == 1


def test_schema_validate_passes(runner, vault_file):
    runner.invoke(schema_group, ["define", "DB_URL", vault_file])
    result = runner.invoke(schema_group, ["validate", vault_file, "secret"])
    assert result.exit_code == 0
    assert "validates" in result.output


def test_schema_validate_missing_required(runner, vault_file):
    runner.invoke(schema_group, ["define", "MISSING_KEY", vault_file])
    result = runner.invoke(schema_group, ["validate", vault_file, "secret"])
    assert result.exit_code == 1
    assert "MISSING_KEY" in result.output
