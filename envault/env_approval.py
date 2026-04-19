import json
import os
from datetime import datetime

APPROVAL_FILENAME = ".envault_approvals.json"
VALID_STATUSES = ["pending", "approved", "rejected"]


class ApprovalError(Exception):
    pass


def _approval_path(vault_dir: str) -> str:
    return os.path.join(vault_dir, APPROVAL_FILENAME)


def _load_approvals(vault_dir: str) -> dict:
    path = _approval_path(vault_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_approvals(vault_dir: str, data: dict) -> None:
    path = _approval_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def request_approval(vault_dir: str, key: str, requester: str) -> dict:
    data = _load_approvals(vault_dir)
    entry = {
        "status": "pending",
        "requester": requester,
        "requested_at": datetime.utcnow().isoformat(),
        "reviewed_by": None,
        "reviewed_at": None,
    }
    data[key] = entry
    _save_approvals(vault_dir, data)
    return entry


def review_approval(vault_dir: str, key: str, reviewer: str, status: str) -> dict:
    if status not in VALID_STATUSES:
        raise ApprovalError(f"Invalid status '{status}'. Must be one of {VALID_STATUSES}")
    data = _load_approvals(vault_dir)
    if key not in data:
        raise ApprovalError(f"No approval request found for key '{key}'")
    data[key]["status"] = status
    data[key]["reviewed_by"] = reviewer
    data[key]["reviewed_at"] = datetime.utcnow().isoformat()
    _save_approvals(vault_dir, data)
    return data[key]


def get_approval(vault_dir: str, key: str) -> dict | None:
    data = _load_approvals(vault_dir)
    return data.get(key)


def list_approvals(vault_dir: str, status: str | None = None) -> dict:
    data = _load_approvals(vault_dir)
    if status is None:
        return data
    return {k: v for k, v in data.items() if v["status"] == status}


def remove_approval(vault_dir: str, key: str) -> None:
    data = _load_approvals(vault_dir)
    if key not in data:
        raise ApprovalError(f"No approval record found for key '{key}'")
    del data[key]
    _save_approvals(vault_dir, data)
