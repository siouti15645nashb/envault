"""Vault diff: compare two vault snapshots or a vault against a .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import list_variables


@dataclass
class DiffResult:
    added: List[str] = field(default_factory=list)      # keys only in right
    removed: List[str] = field(default_factory=list)    # keys only in left
    changed: List[str] = field(default_factory=list)    # keys in both, values differ
    unchanged: List[str] = field(default_factory=list)  # keys in both, values same

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_dicts(left: Dict[str, str], right: Dict[str, str]) -> DiffResult:
    """Compare two plain dicts of env variables and return a DiffResult."""
    left_keys = set(left)
    right_keys = set(right)

    result = DiffResult()
    result.removed = sorted(left_keys - right_keys)
    result.added = sorted(right_keys - left_keys)

    for key in sorted(left_keys & right_keys):
        if left[key] == right[key]:
            result.unchanged.append(key)
        else:
            result.changed.append(key)

    return result


def diff_vault_vs_dotenv(vault_path: str, password: str, dotenv_path: str) -> DiffResult:
    """Compare a vault's variables against a .env file on disk."""
    vault_vars = list_variables(vault_path, password)
    dotenv_vars = parse_dotenv(dotenv_path)
    return diff_dicts(vault_vars, dotenv_vars)


def diff_vaults(vault_path_a: str, password_a: str,
               vault_path_b: str, password_b: str) -> DiffResult:
    """Compare two separate vault files."""
    vars_a = list_variables(vault_path_a, password_a)
    vars_b = list_variables(vault_path_b, password_b)
    return diff_dicts(vars_a, vars_b)


def parse_dotenv(path: str) -> Dict[str, str]:
    """Parse a .env file into a dict, ignoring comments and blank lines."""
    result: Dict[str, str] = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f".env file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                result[key] = value
    return result
