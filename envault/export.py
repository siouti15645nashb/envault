"""Export vault variables to shell-compatible formats."""

from pathlib import Path
from typing import Optional

from envault.vault import list_variables, get_variable


SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_variables(
    vault_path: Path,
    password: str,
    fmt: str = "dotenv",
    keys: Optional[list] = None,
) -> str:
    """Export vault variables as a formatted string.

    Args:
        vault_path: Path to the vault file.
        password: Master password for decryption.
        fmt: Output format — 'dotenv', 'shell', or 'json'.
        keys: Optional list of specific keys to export. Exports all if None.

    Returns:
        A string representation of the variables in the requested format.

    Raises:
        ValueError: If an unsupported format is requested.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    all_keys = list_variables(vault_path, password)
    selected_keys = keys if keys is not None else all_keys

    pairs = {}
    for key in selected_keys:
        pairs[key] = get_variable(vault_path, password, key)

    if fmt == "dotenv":
        return _format_dotenv(pairs)
    elif fmt == "shell":
        return _format_shell(pairs)
    elif fmt == "json":
        return _format_json(pairs)


def _format_dotenv(pairs: dict) -> str:
    """Return KEY=VALUE lines suitable for a .env file."""
    lines = []
    for key, value in pairs.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def _format_shell(pairs: dict) -> str:
    """Return export KEY=VALUE lines suitable for sourcing in bash/zsh."""
    lines = []
    for key, value in pairs.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def _format_json(pairs: dict) -> str:
    """Return a JSON object of key/value pairs."""
    import json
    return json.dumps(pairs, indent=2)
