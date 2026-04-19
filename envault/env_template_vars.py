"""Support for template variable interpolation in vault values."""

import re
from envault.vault import VaultError, get_variable, list_variables

TEMPLATE_PATTERN = re.compile(r"\$\{([^}]+)\}")


class InterpolationError(Exception):
    pass


def _find_refs(value: str) -> list:
    """Return list of variable names referenced in a template string."""
    return TEMPLATE_PATTERN.findall(value)


def interpolate_value(value: str, vault_path: str, password: str, _seen: set = None) -> str:
    """Recursively interpolate ${VAR} references in value using vault contents."""
    if _seen is None:
        _seen = set()

    refs = _find_refs(value)
    if not refs:
        return value

    for ref in refs:
        if ref in _seen:
            raise InterpolationError(f"Circular reference detected: {ref}")
        try:
            ref_value = get_variable(vault_path, password, ref)
        except VaultError as e:
            raise InterpolationError(f"Cannot resolve reference '${{{ref}}}': {e}")
        resolved = interpolate_value(ref_value, vault_path, password, _seen | {ref})
        value = value.replace(f"${{{ref}}}", resolved)

    return value


def interpolate_all(vault_path: str, password: str) -> dict:
    """Return dict of all variables with template references resolved."""
    keys = list_variables(vault_path, password)
    result = {}
    for key in keys:
        raw = get_variable(vault_path, password, key)
        try:
            result[key] = interpolate_value(raw, vault_path, password)
        except InterpolationError:
            result[key] = raw
    return result
