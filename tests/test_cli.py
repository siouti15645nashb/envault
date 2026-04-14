"""Tests for the envault CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_init_success(runner):
    with patch("envault.cli.init_vault") as mock_init:
        result = runner.invoke(cli, ["init"])
        mock_init.assert_called_once()
        assert result.exit_code == 0
        assert "initialized" in result.output


def test_init_already_exists(runner):
    with patch("envault.cli.init_vault", side_effect=FileExistsError("Vault already exists")):
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 1
        assert "Error" in result.output


def test_set_variable_success(runner):
    with patch("envault.cli.set_variable") as mock_set:
        result = runner.invoke(cli, ["set", "MY_KEY", "my_value", "--password", "secret"])
        mock_set.assert_called_once_with("MY_KEY", "my_value", "secret")
        assert result.exit_code == 0
        assert "MY_KEY" in result.output


def test_set_variable_no_vault(runner):
    with patch("envault.cli.set_variable", side_effect=FileNotFoundError):
        result = runner.invoke(cli, ["set", "MY_KEY", "my_value", "--password", "secret"])
        assert result.exit_code == 1
        assert "envault init" in result.output


def test_get_variable_success(runner):
    with patch("envault.cli.get_variable", return_value="my_value"):
        result = runner.invoke(cli, ["get", "MY_KEY", "--password", "secret"])
        assert result.exit_code == 0
        assert "my_value" in result.output


def test_get_variable_not_found(runner):
    with patch("envault.cli.get_variable", return_value=None):
        result = runner.invoke(cli, ["get", "MISSING", "--password", "secret"])
        assert result.exit_code == 1
        assert "not found" in result.output


def test_get_variable_wrong_password(runner):
    with patch("envault.cli.get_variable", side_effect=Exception("decryption error")):
        result = runner.invoke(cli, ["get", "MY_KEY", "--password", "wrong"])
        assert result.exit_code == 1
        assert "Decryption failed" in result.output


def test_list_variables(runner):
    with patch("envault.cli.list_variables", return_value=["KEY_A", "KEY_B"]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "KEY_A" in result.output
        assert "KEY_B" in result.output


def test_list_variables_empty(runner):
    with patch("envault.cli.list_variables", return_value=[]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No variables" in result.output


def test_delete_variable_success(runner):
    with patch("envault.cli.delete_variable", return_value=True):
        result = runner.invoke(cli, ["delete", "MY_KEY"])
        assert result.exit_code == 0
        assert "deleted" in result.output


def test_delete_variable_not_found(runner):
    with patch("envault.cli.delete_variable", return_value=False):
        result = runner.invoke(cli, ["delete", "MISSING"])
        assert result.exit_code == 1
        assert "not found" in result.output
