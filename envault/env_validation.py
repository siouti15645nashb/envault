"""Validation rules for environment variable values."""

import re
from dataclasses import dataclass, field
from typing import Optional

VALIDATION_FILENAME = ".envault_validation.json"


class ValidationError(Exception):
    pass


@dataclass
class ValidationResult:
    key: str
    passed: bool
    rule: Optional[str] = None
    message: Optional[str] = None


def has_failures(results: list) -> bool:
    return any(not r.passed for r in results)


VALIDATION_RULES = {
    "nonempty": lambda v: (bool(v.strip()), "Value must not be empty"),
    "numeric": lambda v: (v.strip().lstrip('-').replace('.', '', 1).isdigit(), "Value must be numeric"),
    "alphanumeric": lambda v: (v.strip().isalnum(), "Value must be alphanumeric"),
    "url": lambda v: (bool(re.match(r'^https?://', v.strip())), "Value must be a URL starting with http(s)://"),
    "email": lambda v: (bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', v.strip())), "Value must be a valid email"),
    "min_length_8": lambda v: (len(v) >= 8, "Value must be at least 8 characters"),
}


def validate_value(key: str, value: str, rules: list) -> list:
    results = []
    for rule in rules:
        if rule not in VALIDATION_RULES:
            raise ValidationError(f"Unknown validation rule: {rule}")
        passed, message = VALIDATION_RULES[rule](value)
        results.append(ValidationResult(key=key, passed=passed, rule=rule, message=message if not passed else None))
    return results


def validate_all(variables: dict, rule_map: dict) -> list:
    """Validate multiple variables against their assigned rules.
    variables: {key: plaintext_value}
    rule_map: {key: [rule, ...]}
    """
    results = []
    for key, rules in rule_map.items():
        value = variables.get(key, "")
        results.extend(validate_value(key, value, rules))
    return results
