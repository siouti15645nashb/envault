"""Group-based variable organization for envault."""

import json
from pathlib import Path
from typing import Dict, List, Optional

GROUPS_FILENAME = ".envault_groups.json"


class GroupError(Exception):
    pass


def _groups_path(vault_dir: str) -> Path:
    return Path(vault_dir) / GROUPS_FILENAME


def _load_groups(vault_dir: str) -> Dict[str, List[str]]:
    path = _groups_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_groups(vault_dir: str, groups: Dict[str, List[str]]) -> None:
    path = _groups_path(vault_dir)
    with open(path, "w") as f:
        json.dump(groups, f, indent=2)


def add_to_group(vault_dir: str, group: str, key: str) -> None:
    if not group.strip():
        raise GroupError("Group name cannot be empty.")
    if not key.strip():
        raise GroupError("Key cannot be empty.")
    groups = _load_groups(vault_dir)
    members = groups.setdefault(group, [])
    if key not in members:
        members.append(key)
    _save_groups(vault_dir, groups)


def remove_from_group(vault_dir: str, group: str, key: str) -> None:
    groups = _load_groups(vault_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    if key not in groups[group]:
        raise GroupError(f"Key '{key}' is not in group '{group}'.")
    groups[group].remove(key)
    if not groups[group]:
        del groups[group]
    _save_groups(vault_dir, groups)


def list_groups(vault_dir: str) -> Dict[str, List[str]]:
    return _load_groups(vault_dir)


def get_group_members(vault_dir: str, group: str) -> List[str]:
    groups = _load_groups(vault_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    return list(groups[group])


def delete_group(vault_dir: str, group: str) -> None:
    groups = _load_groups(vault_dir)
    if group not in groups:
        raise GroupError(f"Group '{group}' does not exist.")
    del groups[group]
    _save_groups(vault_dir, groups)


def find_groups_for_key(vault_dir: str, key: str) -> List[str]:
    groups = _load_groups(vault_dir)
    return [g for g, members in groups.items() if key in members]
