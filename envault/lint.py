"""Lint/validate environment variable names and values in the vault."""

import re
from typing import List, NamedTuple

from envault.vault import list_variables, VaultError

LINT_RULES = [
    "naming",
    "empty_value",
    "whitespace",
    "duplicate_prefix",
]


class LintIssue(NamedTuple):
    key: str
    rule: str
    message: str
    severity: str  # "error" or "warning"


_VALID_NAME_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')


def _check_naming(key: str) -> List[LintIssue]:
    issues = []
    if not _VALID_NAME_RE.match(key):
        issues.append(LintIssue(
            key=key,
            rule="naming",
            message=f"'{key}' should be UPPER_SNAKE_CASE (A-Z, 0-9, underscore, not starting with digit)",
            severity="error",
        ))
    return issues


def _check_empty_value(key: str, value: str) -> List[LintIssue]:
    if value == "":
        return [LintIssue(key=key, rule="empty_value",
                          message=f"'{key}' has an empty value", severity="warning")]
    return []


def _check_whitespace(key: str, value: str) -> List[LintIssue]:
    issues = []
    if value != value.strip():
        issues.append(LintIssue(key=key, rule="whitespace",
                                message=f"'{key}' value has leading or trailing whitespace",
                                severity="warning"))
    return issues


def _check_duplicate_prefix(keys: List[str]) -> List[LintIssue]:
    """Warn when a key is itself a prefix of another key with no separator."""
    issues = []
    sorted_keys = sorted(keys)
    for i, key in enumerate(sorted_keys):
        for other in sorted_keys[i + 1:]:
            if other.startswith(key) and not other[len(key):].startswith("_"):
                issues.append(LintIssue(
                    key=key,
                    rule="duplicate_prefix",
                    message=f"'{key}' is a bare prefix of '{other}' — consider using underscore separation",
                    severity="warning",
                ))
                break
    return issues


def _check_double_underscore(key: str) -> List[LintIssue]:
    """Warn when a key contains consecutive underscores, which is likely a typo."""
    if "__" in key:
        return [LintIssue(
            key=key,
            rule="naming",
            message=f"'{key}' contains consecutive underscores, which may be a typo",
            severity="warning",
        )]
    return []


def lint_vault(vault_path: str, password: str) -> List[LintIssue]:
    """Run all lint rules against the vault and return a list of issues."""
    variables = list_variables(vault_path, password)
    issues: List[LintIssue] = []
    for key, value in variables.items():
        issues.extend(_check_naming(key))
        issues.extend(_check_double_underscore(key))
        issues.extend(_check_empty_value(key, value))
        issues.extend(_check_whitespace(key, value))
    issues.extend(_check_duplicate_prefix(list(variables.keys())))
    return issues
