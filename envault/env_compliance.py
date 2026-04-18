import json
from pathlib import Path

COMPLIANCE_FILENAME = ".envault_compliance.json"

VALID_STANDARDS = ["gdpr", "hipaa", "pci", "sox", "custom"]


class ComplianceError(Exception):
    pass


def _compliance_path(vault_path: str) -> Path:
    return Path(vault_path).parent / COMPLIANCE_FILENAME


def _load_compliance(vault_path: str) -> dict:
    p = _compliance_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_compliance(vault_path: str, data: dict) -> None:
    p = _compliance_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_compliance(vault_path: str, key: str, standard: str, note: str = "") -> None:
    if standard not in VALID_STANDARDS:
        raise ComplianceError(f"Unknown standard '{standard}'. Valid: {VALID_STANDARDS}")
    data = _load_compliance(vault_path)
    data[key] = {"standard": standard, "note": note}
    _save_compliance(vault_path, data)


def remove_compliance(vault_path: str, key: str) -> None:
    data = _load_compliance(vault_path)
    if key not in data:
        raise ComplianceError(f"No compliance entry for '{key}'")
    del data[key]
    _save_compliance(vault_path, data)


def get_compliance(vault_path: str, key: str) -> dict | None:
    data = _load_compliance(vault_path)
    return data.get(key)


def list_compliance(vault_path: str) -> dict:
    return _load_compliance(vault_path)
