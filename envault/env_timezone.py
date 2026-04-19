import json
import os
from typing import Dict, Optional

TIMEZONE_FILENAME = ".envault_timezone"

VALID_TIMEZONES = [
    "UTC", "America/New_York", "America/Chicago", "America/Denver",
    "America/Los_Angeles", "Europe/London", "Europe/Paris", "Europe/Berlin",
    "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Australia/Sydney",
]


class TimezoneError(Exception):
    pass


def _timezone_path(vault_path: str) -> str:
    directory = os.path.dirname(os.path.abspath(vault_path))
    return os.path.join(directory, TIMEZONE_FILENAME)


def _load_timezones(vault_path: str) -> Dict[str, str]:
    path = _timezone_path(vault_path)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_timezones(vault_path: str, data: Dict[str, str]) -> None:
    path = _timezone_path(vault_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_timezone(vault_path: str, key: str, timezone: str) -> None:
    if timezone not in VALID_TIMEZONES:
        raise TimezoneError(
            f"Invalid timezone '{timezone}'. Valid options: {', '.join(VALID_TIMEZONES)}"
        )
    data = _load_timezones(vault_path)
    data[key] = timezone
    _save_timezones(vault_path, data)


def get_timezone(vault_path: str, key: str) -> Optional[str]:
    data = _load_timezones(vault_path)
    return data.get(key)


def remove_timezone(vault_path: str, key: str) -> None:
    data = _load_timezones(vault_path)
    if key not in data:
        raise TimezoneError(f"No timezone set for '{key}'")
    del data[key]
    _save_timezones(vault_path, data)


def list_timezones(vault_path: str) -> Dict[str, str]:
    return _load_timezones(vault_path)
