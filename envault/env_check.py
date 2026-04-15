"""env_check.py — Compare vault variables against the current process environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os

from envault.vault import list_variables, VaultError


@dataclass
class EnvCheckResult:
    missing: List[str] = field(default_factory=list)   # in vault, not in env
    extra: List[str] = field(default_factory=list)     # in env, not in vault
    mismatched: List[str] = field(default_factory=list)  # in both but different value
    matched: List[str] = field(default_factory=list)   # in both and same value

    @property
    def has_issues(self) -> bool:
        return bool(self.missing or self.mismatched)


def check_env(
    vault_path: str,
    password: str,
    env: Optional[Dict[str, str]] = None,
    *,
    include_extra: bool = False,
) -> EnvCheckResult:
    """Compare vault variables against *env* (defaults to ``os.environ``).

    Parameters
    ----------
    vault_path:
        Path to the ``.envault`` file.
    password:
        Master password used to decrypt the vault.
    env:
        Mapping to compare against; defaults to ``os.environ``.
    include_extra:
        When *True*, populate ``result.extra`` with keys present in *env* but
        not in the vault.  Off by default to avoid leaking unrelated env vars.
    """
    if env is None:
        env = dict(os.environ)

    vault_vars: Dict[str, str] = list_variables(vault_path, password)
    result = EnvCheckResult()

    for key, vault_val in vault_vars.items():
        if key not in env:
            result.missing.append(key)
        elif env[key] != vault_val:
            result.mismatched.append(key)
        else:
            result.matched.append(key)

    if include_extra:
        vault_keys = set(vault_vars.keys())
        for key in env:
            if key not in vault_keys:
                result.extra.append(key)

    # Stable ordering
    result.missing.sort()
    result.mismatched.sort()
    result.matched.sort()
    result.extra.sort()

    return result
