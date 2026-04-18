"""Tests for envault.env_format and cli_format."""

import pytest
from click.testing import CliRunner
from envault.env_format import (
    set_format, remove_format, get_format, list_formats,
    validate_format, FormatError, FORMAT_FILENAME, SUPPORTED_FORMATS
)
from envault.vault import init_vault
from envault.cli_format import format_group


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    return path


def test_format_filename_constant():
    assert FORMAT_FILENAME == ".envault_formats.json"


def test_supported_formats_includes_common():
    for fmt in ["uppercase", "lowercase", "numeric", "email", "url"]:
        assert fmt in SUPPORTED_FORMATS


def test_list_formats_empty_when_no_file(vault_file):
    assert list_formats(vault_file) == {}


def test_set_format_creates_entry(vault_file):
    set_format(vault_file, "MY_KEY", "uppercase")
    assert get_format(vault_file, "MY_KEY") == "uppercase"


def test_set_format_invalid_raises(vault_file):
    with pytest.raises(FormatError):
        set_format(vault_file, "KEY", "nonexistent_format")


def test_remove_format(vault_file):
    set_format(vault_file, "KEY", "numeric")
    remove_format(vault_file, "KEY")
    assert get_format(vault_file, "KEY") is None


def test_remove_format_nonexistent_is_noop(vault_file):
    remove_format(vault_file, "MISSING")  # should not raise


def test_list_formats_returns_all(vault_file):
    set_format(vault_file, "A", "uppercase")
    set_format(vault_file, "B", "numeric")
    result = list_formats(vault_file)
    assert result == {"A": "uppercase", "B": "numeric"}


def test_validate_format_uppercase_pass():
    assert validate_format("HELLO_123", "uppercase") is True


def test_validate_format_uppercase_fail():
    assert validate_format("hello", "uppercase") is False


def test_validate_format_numeric_pass():
    assert validate_format("3.14", "numeric") is True


def test_validate_format_email_pass():
    assert validate_format("user@example.com", "email") is True


def test_validate_format_email_fail():
    assert validate_format("not-an-email", "email") is False


def test_validate_format_unknown_raises():
    with pytest.raises(FormatError):
        validate_format("value", "unknown")


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_format_set_success(runner, vault_file):
    result = runner.invoke(format_group, ["set", "MY_KEY", "lowercase", "--vault", vault_file])
    assert result.exit_code == 0
    assert "lowercase" in result.output


def test_cli_format_set_invalid(runner, vault_file):
    result = runner.invoke(format_group, ["set", "MY_KEY", "bad_fmt", "--vault", vault_file])
    assert result.exit_code == 1


def test_cli_format_list_empty(runner, vault_file):
    result = runner.invoke(format_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No format rules" in result.output


def test_cli_format_list_shows_entries(runner, vault_file):
    set_format(vault_file, "PORT", "numeric")
    result = runner.invoke(format_group, ["list", "--vault", vault_file])
    assert "PORT" in result.output
    assert "numeric" in result.output
