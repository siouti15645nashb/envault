"""Variable change history tracking for envault."""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional

HISTORY_FILENAME = ".envault_history.json"
MAX_HISTORY_ENTRIES = 200


class HistoryError(Exception):
    pass


def _history_path(vault_dir: str) -> str:
    return os.path.join(vault_dir, HISTORY_FILENAME)


def _load_history(vault_dir: str) -> List[Dict]:
    path = _history_path(vault_dir)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_history(vault_dir: str, entries: List[Dict]) -> None:
    path = _history_path(vault_dir)
    # Trim to max entries (keep most recent)
    entries = entries[-MAX_HISTORY_ENTRIES:]
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_change(vault_dir: str, key: str, action: str, actor: Optional[str] = None) -> None:
    """Record a variable change event (set, delete, rotate)."""
    if action not in ("set", "delete", "rotate"):
        raise HistoryError(f"Unknown action: {action!r}")
    entries = _load_history(vault_dir)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "key": key,
        "action": action,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    entries.append(entry)
    _save_history(vault_dir, entries)


def get_history(vault_dir: str, key: Optional[str] = None) -> List[Dict]:
    """Return history entries, optionally filtered by key."""
    entries = _load_history(vault_dir)
    if key is not None:
        entries = [e for e in entries if e["key"] == key]
    return entries


def clear_history(vault_dir: str) -> int:
    """Clear all history entries. Returns number of entries removed."""
    entries = _load_history(vault_dir)
    count = len(entries)
    _save_history(vault_dir, [])
    return count
