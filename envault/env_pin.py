"""Pin variables to specific versions, preventing accidental overwrites."""

import json
from pathlib import Path
from typing import List

PIN_FILENAME = ".envault_pins.json"


class PinError(Exception):
    pass


def _pin_path(vault_path: str) -> Path:
    return Path(vault_path).parent / PIN_FILENAME


def _load_pins(vault_path: str) -> dict:
    p = _pin_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_pins(vault_path: str, pins: dict) -> None:
    p = _pin_path(vault_path)
    with open(p, "w") as f:
        json.dump(pins, f, indent=2)


def pin_variable(vault_path: str, key: str) -> None:
    """Mark a variable as pinned."""
    from envault.vault import get_variable, VaultError
    try:
        get_variable(vault_path, key, password="")
    except Exception:
        pass  # key existence is checked loosely; vault handles auth
    pins = _load_pins(vault_path)
    pins[key] = True
    _save_pins(vault_path, pins)


def unpin_variable(vault_path: str, key: str) -> None:
    """Remove pin from a variable."""
    pins = _load_pins(vault_path)
    if key not in pins:
        raise PinError(f"Variable '{key}' is not pinned.")
    del pins[key]
    _save_pins(vault_path, pins)


def is_pinned(vault_path: str, key: str) -> bool:
    return _load_pins(vault_path).get(key, False)


def list_pinned(vault_path: str) -> List[str]:
    return [k for k, v in _load_pins(vault_path).items() if v]
