"""Tests for envault.lint module."""

import pytest
from envault.lint import (
    LintIssue,
    _check_naming,
    _check_empty_value,
    _check_whitespace,
    _check_duplicate_prefix,
    lint_vault,
    LINT_RULES,
)
from envault.vault import init_vault, set_variable


# ---------------------------------------------------------------------------
# Unit tests for individual rules
# ---------------------------------------------------------------------------

def test_lint_rules_constant():
    assert "naming" in LINT_RULES
    assert "empty_value" in LINT_RULES
    assert "whitespace" in LINT_RULES
    assert "duplicate_prefix" in LINT_RULES


def test_check_naming_valid():
    assert _check_naming("DATABASE_URL") == []
    assert _check_naming("MY_VAR_2") == []


def test_check_naming_lowercase():
    issues = _check_naming("database_url")
    assert len(issues) == 1
    assert issues[0].rule == "naming"
    assert issues[0].severity == "error"


def test_check_naming_starts_with_digit():
    issues = _check_naming("1BAD")
    assert len(issues) == 1
    assert issues[0].rule == "naming"


def test_check_naming_hyphen():
    issues = _check_naming("MY-VAR")
    assert len(issues) == 1


def test_check_empty_value_non_empty():
    assert _check_empty_value("KEY", "value") == []


def test_check_empty_value_empty():
    issues = _check_empty_value("KEY", "")
    assert len(issues) == 1
    assert issues[0].rule == "empty_value"
    assert issues[0].severity == "warning"


def test_check_whitespace_clean():
    assert _check_whitespace("KEY", "clean") == []


def test_check_whitespace_leading():
    issues = _check_whitespace("KEY", " value")
    assert len(issues) == 1
    assert issues[0].rule == "whitespace"
    assert issues[0].severity == "warning"


def test_check_whitespace_trailing():
    issues = _check_whitespace("KEY", "value ")
    assert len(issues) == 1


def test_check_duplicate_prefix_no_issue():
    issues = _check_duplicate_prefix(["DB_HOST", "DB_PORT", "APP_SECRET"])
    assert issues == []


def test_check_duplicate_prefix_detects_bare_prefix():
    issues = _check_duplicate_prefix(["DB", "DBHOST"])
    assert any(i.rule == "duplicate_prefix" for i in issues)


def test_check_duplicate_prefix_underscore_ok():
    # DB and DB_HOST are fine — separated by underscore
    issues = _check_duplicate_prefix(["DB", "DB_HOST"])
    assert issues == []


# ---------------------------------------------------------------------------
# Integration test using a real vault file
# ---------------------------------------------------------------------------

@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "password")
    return path


def test_lint_vault_no_issues_clean_vault(vault_file):
    set_variable(vault_file, "password", "DATABASE_URL", "postgres://localhost/db")
    set_variable(vault_file, "password", "SECRET_KEY", "abc123")
    issues = lint_vault(vault_file, "password")
    assert issues == []


def test_lint_vault_detects_bad_name(vault_file):
    set_variable(vault_file, "password", "badName", "value")
    issues = lint_vault(vault_file, "password")
    naming_issues = [i for i in issues if i.rule == "naming"]
    assert len(naming_issues) == 1
    assert naming_issues[0].key == "badName"


def test_lint_vault_detects_empty_value(vault_file):
    set_variable(vault_file, "password", "EMPTY_VAR", "")
    issues = lint_vault(vault_file, "password")
    empty_issues = [i for i in issues if i.rule == "empty_value"]
    assert len(empty_issues) == 1


def test_lint_vault_returns_list(vault_file):
    result = lint_vault(vault_file, "password")
    assert isinstance(result, list)
