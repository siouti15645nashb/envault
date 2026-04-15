"""Template management for envault: save and apply variable templates."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

TEMPLATES_FILENAME = ".envault_templates.json"


class TemplateError(Exception):
    pass


def _templates_path(directory: str = ".") -> Path:
    return Path(directory) / TEMPLATES_FILENAME


def _load_templates(directory: str = ".") -> Dict[str, List[str]]:
    path = _templates_path(directory)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_templates(templates: Dict[str, List[str]], directory: str = ".") -> None:
    path = _templates_path(directory)
    with open(path, "w") as f:
        json.dump(templates, f, indent=2)


def save_template(name: str, keys: List[str], directory: str = ".") -> None:
    """Save a named template containing a list of variable keys."""
    if not name:
        raise TemplateError("Template name cannot be empty.")
    if not keys:
        raise TemplateError("Template must contain at least one key.")
    templates = _load_templates(directory)
    templates[name] = list(keys)
    _save_templates(templates, directory)


def delete_template(name: str, directory: str = ".") -> None:
    """Delete a named template."""
    templates = _load_templates(directory)
    if name not in templates:
        raise TemplateError(f"Template '{name}' does not exist.")
    del templates[name]
    _save_templates(templates, directory)


def get_template(name: str, directory: str = ".") -> List[str]:
    """Return the list of keys for a named template."""
    templates = _load_templates(directory)
    if name not in templates:
        raise TemplateError(f"Template '{name}' does not exist.")
    return templates[name]


def list_templates(directory: str = ".") -> Dict[str, List[str]]:
    """Return all saved templates."""
    return _load_templates(directory)


def apply_template(name: str, vault_keys: List[str], directory: str = ".") -> Dict[str, bool]:
    """Check which keys from a template are present in the vault.

    Returns a dict mapping each template key to True (present) or False (missing).
    """
    keys = get_template(name, directory)
    return {key: key in vault_keys for key in keys}
