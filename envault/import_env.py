"""Import variables from a .env file into the vault."""

from pathlib import Path
from typing import Dict, List, Tuple

from envault.vault import VaultError, set_variable, list_variables


class ImportError(Exception):
    pass


def parse_dotenv(path: str) -> Dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs."""
    env_path = Path(path)
    if not env_path.exists():
        raise ImportError(f"File not found: {path}")

    result: Dict[str, str] = {}
    with open(env_path, "r") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ImportError(f"Invalid line {lineno}: '{line}' (missing '=')") 
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key:
                raise ImportError(f"Empty key on line {lineno}")
            result[key] = value
    return result


def import_from_dotenv(
    vault_path: str,
    dotenv_path: str,
    password: str,
    overwrite: bool = False,
) -> Tuple[List[str], List[str]]:
    """Import variables from a .env file into the vault.

    Returns (imported_keys, skipped_keys).
    Raises ImportError or VaultError on failure.
    """
    parsed = parse_dotenv(dotenv_path)
    existing = set(list_variables(vault_path, password))

    imported: List[str] = []
    skipped: List[str] = []

    for key, value in parsed.items():
        if key in existing and not overwrite:
            skipped.append(key)
            continue
        set_variable(vault_path, password, key, value)
        imported.append(key)

    return imported, skipped
