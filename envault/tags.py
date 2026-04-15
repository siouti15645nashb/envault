"""Tag management for envault variables."""

from envault.vault import VaultError, _load_raw, _save_raw

TAGS_KEY = "__tags__"


class TagError(Exception):
    pass


def _get_tags_map(vault_path):
    """Return the tags map from the vault (key -> list of tags)."""
    data = _load_raw(vault_path)
    return data.get(TAGS_KEY, {})


def _save_tags_map(vault_path, tags_map):
    """Persist the tags map into the vault file."""
    data = _load_raw(vault_path)
    data[TAGS_KEY] = tags_map
    _save_raw(vault_path, data)


def add_tag(vault_path, key, tag):
    """Add a tag to a variable. Raises TagError if variable doesn't exist."""
    data = _load_raw(vault_path)
    if key not in data.get("variables", {}):
        raise TagError(f"Variable '{key}' not found in vault.")
    tags_map = _get_tags_map(vault_path)
    tags = tags_map.get(key, [])
    if tag not in tags:
        tags.append(tag)
    tags_map[key] = tags
    _save_tags_map(vault_path, tags_map)


def remove_tag(vault_path, key, tag):
    """Remove a tag from a variable. Raises TagError if tag not present."""
    tags_map = _get_tags_map(vault_path)
    tags = tags_map.get(key, [])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on variable '{key}'.")
    tags.remove(tag)
    tags_map[key] = tags
    _save_tags_map(vault_path, tags_map)


def list_tags(vault_path, key):
    """Return list of tags for a given variable key."""
    tags_map = _get_tags_map(vault_path)
    return tags_map.get(key, [])


def find_by_tag(vault_path, tag):
    """Return list of variable keys that have the given tag."""
    tags_map = _get_tags_map(vault_path)
    return [key for key, tags in tags_map.items() if tag in tags]


def all_tags(vault_path):
    """Return a sorted list of all unique tags used across all variables."""
    tags_map = _get_tags_map(vault_path)
    unique = set()
    for tags in tags_map.values():
        unique.update(tags)
    return sorted(unique)
