"""Profile management for envault — named sets of variables for different environments."""

import json
from pathlib import Path
from typing import Dict, List, Optional

PROFILES_FILENAME = ".envault_profiles.json"


class ProfileError(Exception):
    pass


def _profiles_path(directory: str = ".") -> Path:
    return Path(directory) / PROFILES_FILENAME


def _load_profiles(directory: str = ".") -> Dict:
    path = _profiles_path(directory)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_profiles(profiles: Dict, directory: str = ".") -> None:
    path = _profiles_path(directory)
    with open(path, "w") as f:
        json.dump(profiles, f, indent=2)


def save_profile(name: str, keys: List[str], directory: str = ".") -> None:
    """Save a named profile containing a list of variable keys."""
    if not name or not name.strip():
        raise ProfileError("Profile name must not be empty.")
    if not isinstance(keys, list):
        raise ProfileError("Keys must be a list.")
    profiles = _load_profiles(directory)
    profiles[name] = list(keys)
    _save_profiles(profiles, directory)


def delete_profile(name: str, directory: str = ".") -> None:
    """Delete a named profile."""
    profiles = _load_profiles(directory)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' does not exist.")
    del profiles[name]
    _save_profiles(profiles, directory)


def list_profiles(directory: str = ".") -> List[str]:
    """Return all profile names."""
    return list(_load_profiles(directory).keys())


def get_profile(name: str, directory: str = ".") -> List[str]:
    """Return the list of keys in a named profile."""
    profiles = _load_profiles(directory)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' does not exist.")
    return profiles[name]


def apply_profile(
    name: str,
    password: str,
    vault_path: str = ".envault",
    directory: str = ".",
) -> Dict[str, Optional[str]]:
    """Return a dict of key->value for all keys in the profile, reading from the vault."""
    from envault.vault import get_variable, VaultError

    keys = get_profile(name, directory)
    result = {}
    for key in keys:
        try:
            result[key] = get_variable(key, password, vault_path)
        except VaultError:
            result[key] = None
    return result
