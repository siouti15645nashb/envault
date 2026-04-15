"""Tests for envault/cli_profiles.py"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envault.cli_profiles import profiles_group
from envault.profiles import save_profile


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmpdir_str(tmp_path):
    return str(tmp_path)


def test_profile_save_success(runner, tmpdir_str):
    result = runner.invoke(
        profiles_group, ["save", "dev", "KEY1", "KEY2", "--dir", tmpdir_str]
    )
    assert result.exit_code == 0
    assert "saved" in result.output
    assert "2 key(s)" in result.output


def test_profile_save_empty_name_fails(runner, tmpdir_str):
    result = runner.invoke(
        profiles_group, ["save", "", "KEY1", "--dir", tmpdir_str]
    )
    assert result.exit_code != 0


def test_profile_list_empty(runner, tmpdir_str):
    result = runner.invoke(profiles_group, ["list", "--dir", tmpdir_str])
    assert result.exit_code == 0
    assert "No profiles" in result.output


def test_profile_list_shows_names(runner, tmpdir_str):
    save_profile("dev", ["A"], tmpdir_str)
    save_profile("prod", ["B"], tmpdir_str)
    result = runner.invoke(profiles_group, ["list", "--dir", tmpdir_str])
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "prod" in result.output


def test_profile_show_keys(runner, tmpdir_str):
    save_profile("dev", ["DB_URL", "SECRET"], tmpdir_str)
    result = runner.invoke(profiles_group, ["show", "dev", "--dir", tmpdir_str])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "SECRET" in result.output


def test_profile_show_nonexistent(runner, tmpdir_str):
    result = runner.invoke(profiles_group, ["show", "ghost", "--dir", tmpdir_str])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_profile_delete_success(runner, tmpdir_str):
    save_profile("dev", ["KEY1"], tmpdir_str)
    result = runner.invoke(profiles_group, ["delete", "dev", "--dir", tmpdir_str])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_profile_delete_nonexistent(runner, tmpdir_str):
    result = runner.invoke(profiles_group, ["delete", "ghost", "--dir", tmpdir_str])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_profile_apply_outputs_values(runner, tmpdir_str):
    save_profile("dev", ["DB_URL"], tmpdir_str)
    with patch("envault.profiles.get_variable") as mock_get:
        mock_get.return_value = "postgres://localhost/db"
        result = runner.invoke(
            profiles_group,
            ["apply", "dev", "--password", "secret", "--dir", tmpdir_str],
        )
    assert result.exit_code == 0
    assert "DB_URL=postgres://localhost/db" in result.output
