"""Compare variables across two vault files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set
from envault.vault import get_variable, list_variables, VaultError


@dataclass
class CompareResult:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    same: List[str] = field(default_factory=list)
    different: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.different)


class CompareError(Exception):
    pass


def compare_vaults(vault_a: str, password_a: str, vault_b: str, password_b: str) -> CompareResult:
    """Compare all variables between two vaults."""
    try:
        keys_a: Set[str] = set(list_variables(vault_a, password_a))
    except VaultError as e:
        raise CompareError(f"Error reading vault A: {e}") from e

    try:
        keys_b: Set[str] = set(list_variables(vault_b, password_b))
    except VaultError as e:
        raise CompareError(f"Error reading vault B: {e}") from e

    result = CompareResult()
    result.only_in_a = sorted(keys_a - keys_b)
    result.only_in_b = sorted(keys_b - keys_a)

    for key in sorted(keys_a & keys_b):
        val_a = get_variable(vault_a, password_a, key)
        val_b = get_variable(vault_b, password_b, key)
        if val_a == val_b:
            result.same.append(key)
        else:
            result.different.append(key)

    return result


def compare_summary(result: CompareResult) -> Dict[str, int]:
    return {
        "only_in_a": len(result.only_in_a),
        "only_in_b": len(result.only_in_b),
        "same": len(result.same),
        "different": len(result.different),
    }
