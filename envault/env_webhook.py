import json
import os
from pathlib import Path

WEBHOOK_FILENAME = ".envault_webhooks.json"


class WebhookError(Exception):
    pass


def _webhook_path(vault_path: str) -> Path:
    return Path(vault_path).parent / WEBHOOK_FILENAME


def _load_webhooks(vault_path: str) -> dict:
    p = _webhook_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_webhooks(vault_path: str, data: dict) -> None:
    p = _webhook_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def add_webhook(vault_path: str, name: str, url: str, events: list = None) -> None:
    if not name or not name.strip():
        raise WebhookError("Webhook name cannot be empty.")
    if not url or not url.strip():
        raise WebhookError("Webhook URL cannot be empty.")
    data = _load_webhooks(vault_path)
    data[name] = {"url": url, "events": events or ["set", "delete", "rotate"]}
    _save_webhooks(vault_path, data)


def remove_webhook(vault_path: str, name: str) -> None:
    data = _load_webhooks(vault_path)
    if name not in data:
        raise WebhookError(f"Webhook '{name}' not found.")
    del data[name]
    _save_webhooks(vault_path, data)


def list_webhooks(vault_path: str) -> dict:
    return _load_webhooks(vault_path)


def get_webhook(vault_path: str, name: str) -> dict:
    data = _load_webhooks(vault_path)
    if name not in data:
        raise WebhookError(f"Webhook '{name}' not found.")
    return data[name]
