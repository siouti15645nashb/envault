"""Tests for env_regex module and CLI."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.env_regex import (
    REGEX_FILENAME,
    RegexError,
    set_pattern,
    remove_pattern,
    get_pattern,
    list_patterns,
    validate_against_pattern,
)
from envault.cli_regex import regex_group


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".envault"
    v.write_text('{"salt": "abc", "variables": {}}')
    return str(v)


@pytest.fixture
def runner():
    return CliRunner()


def test_regex_filename_constant():
    assert REGEX_FILENAME == ".envault_regex.json"


def test_list_patterns_empty_when_no_file(vault_file):
    assert list_patterns(vault_file) == {}


def test_set_pattern_creates_file(vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    p = Path(vault_file).parent / REGEX_FILENAME
    assert p.exists()


def test_set_pattern_stores_entry(vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    assert get_pattern(vault_file, "PORT") == r"\d+"


def test_get_pattern_none_when_missing(vault_file):
    assert get_pattern(vault_file, "MISSING") is None


def test_set_invalid_pattern_raises(vault_file):
    with pytest.raises(RegexError):
        set_pattern(vault_file, "KEY", "[invalid")


def test_remove_pattern_success(vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    remove_pattern(vault_file, "PORT")
    assert get_pattern(vault_file, "PORT") is None


def test_remove_nonexistent_raises(vault_file):
    with pytest.raises(RegexError):
        remove_pattern(vault_file, "GHOST")


def test_validate_passes_when_no_pattern(vault_file):
    assert validate_against_pattern(vault_file, "KEY", "anything") is True


def test_validate_passes_matching_value(vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    assert validate_against_pattern(vault_file, "PORT", "8080") is True


def test_validate_fails_non_matching_value(vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    assert validate_against_pattern(vault_file, "PORT", "abc") is False


def test_cli_set_success(runner, vault_file):
    result = runner.invoke(regex_group, ["set", "EMAIL", r".+@.+", "--vault", vault_file])
    assert result.exit_code == 0
    assert "EMAIL" in result.output


def test_cli_set_invalid_pattern(runner, vault_file):
    result = runner.invoke(regex_group, ["set", "KEY", "[bad", "--vault", vault_file])
    assert result.exit_code != 0


def test_cli_list_shows_patterns(runner, vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    result = runner.invoke(regex_group, ["list", "--vault", vault_file])
    assert "PORT" in result.output


def test_cli_check_ok(runner, vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    result = runner.invoke(regex_group, ["check", "PORT", "9000", "--vault", vault_file])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_cli_check_fail(runner, vault_file):
    set_pattern(vault_file, "PORT", r"\d+")
    result = runner.invoke(regex_group, ["check", "PORT", "notanumber", "--vault", vault_file])
    assert result.exit_code != 0
