"""Tests for envault/env_validation.py"""

import pytest
from envault.env_validation import (
    ValidationError, ValidationResult, has_failures,
    validate_value, validate_all, VALIDATION_RULES
)


def test_validation_rules_constant():
    assert isinstance(VALIDATION_RULES, dict)
    assert "nonempty" in VALIDATION_RULES
    assert "numeric" in VALIDATION_RULES
    assert "url" in VALIDATION_RULES


def test_validate_value_nonempty_pass():
    results = validate_value("KEY", "hello", ["nonempty"])
    assert len(results) == 1
    assert results[0].passed is True


def test_validate_value_nonempty_fail():
    results = validate_value("KEY", "  ", ["nonempty"])
    assert results[0].passed is False
    assert results[0].message is not None


def test_validate_value_numeric_pass():
    results = validate_value("PORT", "8080", ["numeric"])
    assert results[0].passed is True


def test_validate_value_numeric_fail():
    results = validate_value("PORT", "abc", ["numeric"])
    assert results[0].passed is False


def test_validate_value_url_pass():
    results = validate_value("URL", "https://example.com", ["url"])
    assert results[0].passed is True


def test_validate_value_url_fail():
    results = validate_value("URL", "not-a-url", ["url"])
    assert results[0].passed is False


def test_validate_value_email_pass():
    results = validate_value("EMAIL", "user@example.com", ["email"])
    assert results[0].passed is True


def test_validate_value_email_fail():
    results = validate_value("EMAIL", "notanemail", ["email"])
    assert results[0].passed is False


def test_validate_value_min_length_pass():
    results = validate_value("SECRET", "longpassword", ["min_length_8"])
    assert results[0].passed is True


def test_validate_value_min_length_fail():
    results = validate_value("SECRET", "short", ["min_length_8"])
    assert results[0].passed is False


def test_validate_value_unknown_rule_raises():
    with pytest.raises(ValidationError, match="Unknown validation rule"):
        validate_value("KEY", "val", ["nonexistent_rule"])


def test_validate_all_multiple_keys():
    variables = {"A": "hello", "B": ""}
    rule_map = {"A": ["nonempty"], "B": ["nonempty"]}
    results = validate_all(variables, rule_map)
    assert len(results) == 2
    passed = {r.key: r.passed for r in results}
    assert passed["A"] is True
    assert passed["B"] is False


def test_has_failures_true():
    results = [ValidationResult("K", False, "nonempty", "msg")]
    assert has_failures(results) is True


def test_has_failures_false():
    results = [ValidationResult("K", True, "nonempty", None)]
    assert has_failures(results) is False


def test_validate_all_missing_key_uses_empty_string():
    variables = {}
    rule_map = {"MISSING": ["nonempty"]}
    results = validate_all(variables, rule_map)
    assert results[0].passed is False
