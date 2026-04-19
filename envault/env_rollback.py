import json
from pathlib import Path
from envault.vault import VaultError, _load_raw, _save_raw
from envault.history import _history_path, _load_history

ROLLBACK_FILENAME = ".envault_rollback.json"


class RollbackError(Exception):
    pass


def _rollback_path(vault_path: str) -> Path:
    return Path(vault_path).parent / ROLLBACK_FILENAME


def _load_rollback(vault_path: str) -> list:
    p = _rollback_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_rollback(vault_path: str, data: list) -> None:
    _rollback_path(vault_path).write_text(json.dumps(data, indent=2))


def create_snapshot(vault_path: str, label: str = "") -> dict:
    """Save a named snapshot of the current vault state."""
    raw = _load_raw(vault_path)
    snapshots = _load_rollback(vault_path)
    import time
    snapshot = {
        "label": label,
        "timestamp": time.time(),
        "variables": raw.get("variables", {}),
    }
    snapshots.append(snapshot)
    _save_rollback(vault_path, snapshots)
    return snapshot


def list_snapshots(vault_path: str) -> list:
    """Return all saved snapshots."""
    return _load_rollback(vault_path)


def rollback_to(vault_path: str, index: int, password: str) -> int:
    """Restore vault variables from snapshot at given index."""
    snapshots = _load_rollback(vault_path)
    if not snapshots:
        raise RollbackError("No snapshots available.")
    if index < 0 or index >= len(snapshots):
        raise RollbackError(f"Snapshot index {index} out of range (0-{len(snapshots)-1}).")
    snapshot = snapshots[index]
    from envault.vault import set_variable
    raw = _load_raw(vault_path)
    raw["variables"] = {}
    _save_raw(vault_path, raw)
    restored = snapshot["variables"]
    for key, enc_value in restored.items():
        from envault.crypto import decrypt
        import base64
        salt = bytes.fromhex(raw["salt"])
        from envault.crypto import derive_key
        key_bytes = derive_key(password, salt)
        value = decrypt(key_bytes, enc_value)
        set_variable(vault_path, password, key, value)
    return len(restored)


def delete_snapshot(vault_path: str, index: int) -> None:
    """Remove a snapshot by index."""
    snapshots = _load_rollback(vault_path)
    if index < 0 or index >= len(snapshots):
        raise RollbackError(f"Snapshot index {index} out of range.")
    snapshots.pop(index)
    _save_rollback(vault_path, snapshots)
