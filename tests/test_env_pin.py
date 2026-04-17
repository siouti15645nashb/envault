"""Tests for envault.env_pin and envault.cli_pin."""

import json
import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.env_pin import (
    PIN_FILENAME, pin_variable, unpin_variable, is_pinned, list_pinned, PinError
)
from envault.cli_pin import pin_group


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    set_variable(path, "KEY_A", "value_a", "secret")
    set_variable(path, "KEY_B", "value_b", "secret")
    return path


def test_pin_filename_constant():
    assert PIN_FILENAME == ".envault_pins.json"


def test_is_pinned_false_when_no_file(vault_file):
    assert is_pinned(vault_file, "KEY_A") is False


def test_list_pinned_empty_when_no_file(vault_file):
    assert list_pinned(vault_file) == []


def test_pin_variable_creates_pin_file(vault_file, tmp_path):
    pin_variable(vault_file, "KEY_A")
    pin_file = tmp_path / PIN_FILENAME
    assert pin_file.exists()


def test_pin_variable_marks_key(vault_file):
    pin_variable(vault_file, "KEY_A")
    assert is_pinned(vault_file, "KEY_A") is True


def test_pin_variable_idempotent(vault_file):
    pin_variable(vault_file, "KEY_A")
    pin_variable(vault_file, "KEY_A")
    assert list_pinned(vault_file) == ["KEY_A"]


def test_unpin_variable_removes_pin(vault_file):
    pin_variable(vault_file, "KEY_A")
    unpin_variable(vault_file, "KEY_A")
    assert is_pinned(vault_file, "KEY_A") is False


def test_unpin_nonexistent_raises(vault_file):
    with pytest.raises(PinError):
        unpin_variable(vault_file, "KEY_A")


def test_list_pinned_returns_all(vault_file):
    pin_variable(vault_file, "KEY_A")
    pin_variable(vault_file, "KEY_B")
    assert sorted(list_pinned(vault_file)) == ["KEY_A", "KEY_B"]


def test_cli_pin_add_success(vault_file):
    runner = CliRunner()
    result = runner.invoke(pin_group, ["add", "KEY_A", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Pinned" in result.output


def test_cli_pin_list(vault_file):
    runner = CliRunner()
    pin_variable(vault_file, "KEY_A")
    result = runner.invoke(pin_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "KEY_A" in result.output


def test_cli_pin_remove_success(vault_file):
    runner = CliRunner()
    pin_variable(vault_file, "KEY_A")
    result = runner.invoke(pin_group, ["remove", "KEY_A", "--vault", vault_file])
    assert result.exit_code == 0
    assert "Unpinned" in result.output


def test_cli_pin_check_pinned(vault_file):
    runner = CliRunner()
    pin_variable(vault_file, "KEY_A")
    result = runner.invoke(pin_group, ["check", "KEY_A", "--vault", vault_file])
    assert "is pinned" in result.output
