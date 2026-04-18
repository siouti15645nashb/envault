"""env_status.py — Aggregate status report for a vault."""

import os
from dataclasses import dataclass, field
from typing import List

STATUS_FILENAME = ".envault_status_cache"


@dataclass
class StatusReport:
    vault_path: str
    total_keys: int = 0
    locked_keys: List[str] = field(default_factory=list)
    pinned_keys: List[str] = field(default_factory=list)
    sensitive_keys: List[str] = field(default_factory=list)
    expiring_keys: List[str] = field(default_factory=list)
    readonly_keys: List[str] = field(default_factory=list)
    required_keys: List[str] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.expiring_keys)


def get_status(vault_path: str, password: str) -> StatusReport:
    """Build a StatusReport for the vault at vault_path."""
    from envault.vault import list_variables
    from envault.env_lock import get_locked
    from envault.env_pin import list_pinned
    from envault.env_sensitive import list_sensitive
    from envault.env_readonly import list_readonly
    from envault.env_required import list_required
    from envault.env_expiry import list_expiring
    import datetime

    keys = list_variables(vault_path, password)
    vault_dir = os.path.dirname(os.path.abspath(vault_path))

    expiring = [
        k for k, exp in list_expiring(vault_dir).items()
        if exp <= datetime.datetime.utcnow()
    ]

    return StatusReport(
        vault_path=vault_path,
        total_keys=len(keys),
        locked_keys=list(get_locked(vault_dir)),
        pinned_keys=list(list_pinned(vault_dir)),
        sensitive_keys=list(list_sensitive(vault_dir)),
        expiring_keys=expiring,
        readonly_keys=list(list_readonly(vault_dir)),
        required_keys=list(list_required(vault_dir)),
    )
