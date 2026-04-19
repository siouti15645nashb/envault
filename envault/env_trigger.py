"""env_trigger.py — Define and manage triggers that fire on variable changes."""

import json
import os
from typing import Dict, List, Optional

TRIGGER_FILENAME = ".envault_triggers.json"

VALID_EVENTS = ["on_set", "on_delete", "on_rotate", "on_import", "on_export"]


class TriggerError(Exception):
    """Raised for trigger-related errors."""


def _trigger_path(vault_dir: str) -> str:
    """Return the path to the triggers file."""
    return os.path.join(vault_dir, TRIGGER_FILENAME)


def _load_triggers(vault_dir: str) -> Dict[str, List[Dict]]:
    """Load triggers from disk, returning an empty dict if not found."""
    path = _trigger_path(vault_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_triggers(vault_dir: str, data: Dict[str, List[Dict]]) -> None:
    """Persist triggers to disk."""
    path = _trigger_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_trigger(
    vault_dir: str,
    key: str,
    event: str,
    action: str,
    description: Optional[str] = None,
) -> Dict:
    """Register a trigger for a variable key and event.

    Args:
        vault_dir: Directory containing the vault.
        key: The variable name to watch.
        event: One of VALID_EVENTS.
        action: Shell command or action string to execute.
        description: Optional human-readable description.

    Returns:
        The newly created trigger entry.

    Raises:
        TriggerError: If the event is not valid.
    """
    if event not in VALID_EVENTS:
        raise TriggerError(
            f"Invalid event '{event}'. Valid events: {', '.join(VALID_EVENTS)}"
        )
    data = _load_triggers(vault_dir)
    entry = {"event": event, "action": action}
    if description:
        entry["description"] = description
    data.setdefault(key, []).append(entry)
    _save_triggers(vault_dir, data)
    return entry


def remove_trigger(vault_dir: str, key: str, event: str) -> int:
    """Remove all triggers for a given key and event.

    Returns:
        Number of triggers removed.
    """
    data = _load_triggers(vault_dir)
    if key not in data:
        return 0
    before = len(data[key])
    data[key] = [t for t in data[key] if t["event"] != event]
    removed = before - len(data[key])
    if not data[key]:
        del data[key]
    _save_triggers(vault_dir, data)
    return removed


def list_triggers(vault_dir: str, key: Optional[str] = None) -> Dict[str, List[Dict]]:
    """List all triggers, optionally filtered by key."""
    data = _load_triggers(vault_dir)
    if key is not None:
        return {key: data.get(key, [])}
    return data


def get_triggers_for_event(
    vault_dir: str, key: str, event: str
) -> List[Dict]:
    """Return all triggers registered for a specific key and event."""
    data = _load_triggers(vault_dir)
    return [t for t in data.get(key, []) if t["event"] == event]
