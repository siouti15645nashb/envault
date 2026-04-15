"""Search and filter environment variables in the vault."""

from typing import Optional
from envault.vault import list_variables

SEARCH_ERROR_NO_VAULT = "Vault not found. Run 'envault init' first."


def search_variables(
    vault_path: str,
    password: str,
    pattern: str,
    case_sensitive: bool = False,
) -> dict[str, str]:
    """Return variables whose keys match the given substring pattern.

    Args:
        vault_path: Path to the vault file.
        password: Master password for decryption.
        pattern: Substring to search for in variable names.
        case_sensitive: Whether the search should be case-sensitive.

    Returns:
        A dict of matching key-value pairs.

    Raises:
        FileNotFoundError: If the vault file does not exist.
    """
    all_vars = list_variables(vault_path, password)

    if not case_sensitive:
        pattern = pattern.lower()

    return {
        key: value
        for key, value in all_vars.items()
        if (key if case_sensitive else key.lower()).__contains__(pattern)
    }


def filter_by_prefix(
    vault_path: str,
    password: str,
    prefix: str,
    case_sensitive: bool = False,
) -> dict[str, str]:
    """Return variables whose keys start with the given prefix.

    Args:
        vault_path: Path to the vault file.
        password: Master password for decryption.
        prefix: Prefix to match against variable names.
        case_sensitive: Whether the match should be case-sensitive.

    Returns:
        A dict of matching key-value pairs.

    Raises:
        FileNotFoundError: If the vault file does not exist.
    """
    all_vars = list_variables(vault_path, password)

    if not case_sensitive:
        prefix = prefix.lower()

    return {
        key: value
        for key, value in all_vars.items()
        if (key if case_sensitive else key.lower()).startswith(prefix)
    }
