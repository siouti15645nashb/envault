"""Tests for envault.env_promote and envault.cli_promote."""

import json
import os
import pytest
from click.testing import CliRunner

from envault.vault import init_vault, set_variable, get_variable, list_variables
from envault.env_promote import PromoteError, promote_variables
from envault.cli_promote import promote_group

PASSWORD = "test-password"


@pytest.fixture
def vault_pair(tmp_path):
    src = str(tmp_path / "source.envault")
    dst = str(tmp_path / "dest.envault")
    init_vault(src, PASSWORD)
    init_vault(dst, PASSWORD)
    return src, dst


@pytest.fixture
def runner():
    return Runner()


class Runner:
    def __init__(self):
        self._runner = CliRunner()

    def invoke(self, *args, **kwargs):
        return self._runner.invoke(*args, **kwargs)


def test_promote_all_variables(vault_pair):
    src, dst = vault_pair
    set_variable(src, PASSWORD, "KEY_A", "alpha")
    set_variable(src, PASSWORD, "KEY_B", "beta")
    result = promote_variables(src, dst, PASSWORD)
    assert set(result["promoted"]) == {"KEY_A", "KEY_B"}
    assert result["skipped"] == []
    assert result["failed"] == []
    assert get_variable(dst, PASSWORD, "KEY_A") == "alpha"
    assert get_variable(dst, PASSWORD, "KEY_B") == "beta"


def test_promote_specific_keys(vault_pair):
    src, dst = vault_pair
    set_variable(src, PASSWORD, "KEY_A", "alpha")
    set_variable(src, PASSWORD, "KEY_B", "beta")
    result = promote_variables(src, dst, PASSWORD, keys=["KEY_A"])
    assert result["promoted"] == ["KEY_A"]
    assert "KEY_B" not in list_variables(dst, PASSWORD)


def test_promote_skips_existing_without_overwrite(vault_pair):
    src, dst = vault_pair
    set_variable(src, PASSWORD, "KEY_A", "new_value")
    set_variable(dst, PASSWORD, "KEY_A", "old_value")
    result = promote_variables(src, dst, PASSWORD)
    assert "KEY_A" in result["skipped"]
    assert get_variable(dst, PASSWORD, "KEY_A") == "old_value"


def test_promote_overwrites_when_flag_set(vault_pair):
    src, dst = vault_pair
    set_variable(src, PASSWORD, "KEY_A", "new_value")
    set_variable(dst, PASSWORD, "KEY_A", "old_value")
    result = promote_variables(src, dst, PASSWORD, overwrite=True)
    assert "KEY_A" in result["promoted"]
    assert get_variable(dst, PASSWORD, "KEY_A") == "new_value"


def test_promote_missing_key_reported_as_failed(vault_pair):
    src, dst = vault_pair
    result = promote_variables(src, dst, PASSWORD, keys=["NONEXISTENT"])
    assert len(result["failed"]) == 1
    assert result["failed"][0]["key"] == "NONEXISTENT"


def test_promote_raises_if_source_missing(tmp_path):
    dst = str(tmp_path / "dest.envault")
    init_vault(dst, PASSWORD)
    with pytest.raises(PromoteError, match="Source vault not found"):
        promote_variables(str(tmp_path / "nope.envault"), dst, PASSWORD)


def test_promote_raises_if_dest_missing(tmp_path):
    src = str(tmp_path / "source.envault")
    init_vault(src, PASSWORD)
    with pytest.raises(PromoteError, match="Destination vault not found"):
        promote_variables(src, str(tmp_path / "nope.envault"), PASSWORD)


def test_cli_promote_run_success(vault_pair):
    src, dst = vault_pair
    set_variable(src, PASSWORD, "DB_URL", "postgres://localhost/db")
    cli_runner = CliRunner()
    result = cli_runner.invoke(
        promote_group,
        ["run", src, dst, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "DB_URL" in result.output


def test_cli_promote_run_missing_source(tmp_path):
    dst = str(tmp_path / "dest.envault")
    init_vault(dst, PASSWORD)
    cli_runner = CliRunner()
    result = cli_runner.invoke(
        promote_group,
        ["run", str(tmp_path / "nope.envault"), dst, "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "Error" in result.output or "Error" in (result.output + str(result.exception))
