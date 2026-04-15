"""Audit log support for envault — tracks vault operations with timestamps."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_LOG_FILENAME = ".envault_audit.json"


def _audit_path(vault_dir: str = ".") -> Path:
    return Path(vault_dir) / AUDIT_LOG_FILENAME


def _load_log(vault_dir: str = ".") -> List[dict]:
    path = _audit_path(vault_dir)
    if not path.exists():
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save_log(entries: List[dict], vault_dir: str = ".") -> None:
    path = _audit_path(vault_dir)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_event(
    action: str,
    key: Optional[str] = None,
    actor: Optional[str] = None,
    vault_dir: str = ".",
) -> dict:
    """Append an audit event and return it."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    entries = _load_log(vault_dir)
    entries.append(entry)
    _save_log(entries, vault_dir)
    return entry


def get_log(vault_dir: str = ".") -> List[dict]:
    """Return all audit log entries."""
    return _load_log(vault_dir)


def clear_log(vault_dir: str = ".") -> None:
    """Remove all audit log entries."""
    _save_log([], vault_dir)
