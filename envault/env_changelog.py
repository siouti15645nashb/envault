"""Track a human-readable changelog of vault modifications."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

CHANGELOG_FILENAME = ".envault_changelog.json"


class ChangelogError(Exception):
    pass


def _changelog_path(vault_path: str) -> str:
    directory = os.path.dirname(os.path.abspath(vault_path))
    return os.path.join(directory, CHANGELOG_FILENAME)


def _load_changelog(vault_path: str) -> List[Dict[str, Any]]:
    path = _changelog_path(vault_path)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_changelog(vault_path: str, entries: List[Dict[str, Any]]) -> None:
    path = _changelog_path(vault_path)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def add_entry(
    vault_path: str,
    action: str,
    key: str,
    note: Optional[str] = None,
    author: Optional[str] = None,
) -> Dict[str, Any]:
    """Append a changelog entry for a vault action."""
    entries = _load_changelog(vault_path)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "key": key,
        "note": note or "",
        "author": author or "",
    }
    entries.append(entry)
    _save_changelog(vault_path, entries)
    return entry


def get_changelog(vault_path: str) -> List[Dict[str, Any]]:
    """Return all changelog entries."""
    return _load_changelog(vault_path)


def clear_changelog(vault_path: str) -> int:
    """Clear all changelog entries. Returns number of entries removed."""
    entries = _load_changelog(vault_path)
    count = len(entries)
    _save_changelog(vault_path, [])
    return count
