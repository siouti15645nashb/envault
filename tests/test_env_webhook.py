import json
import pytest
from pathlib import Path
from envault.env_webhook import (
    WEBHOOK_FILENAME,
    WebhookError,
    add_webhook,
    remove_webhook,
    list_webhooks,
    get_webhook,
    _webhook_path,
)
from click.testing import CliRunner
from envault.cli_webhook import webhook_group


@pytest.fixture
def vault_file(tmp_path):
    v = tmp_path / ".envault"
    v.write_text(json.dumps({"salt": "abc", "variables": {}}))
    return str(v)


def test_webhook_filename_constant():
    assert WEBHOOK_FILENAME == ".envault_webhooks.json"


def test_webhook_path_returns_correct_path(vault_file):
    p = _webhook_path(vault_file)
    assert p.name == WEBHOOK_FILENAME


def test_list_webhooks_empty_when_no_file(vault_file):
    assert list_webhooks(vault_file) == {}


def test_add_webhook_creates_file(vault_file):
    add_webhook(vault_file, "slack", "https://hooks.slack.com/abc")
    p = _webhook_path(vault_file)
    assert p.exists()


def test_add_webhook_stores_url(vault_file):
    add_webhook(vault_file, "slack", "https://hooks.slack.com/abc")
    hooks = list_webhooks(vault_file)
    assert "slack" in hooks
    assert hooks["slack"]["url"] == "https://hooks.slack.com/abc"


def test_add_webhook_default_events(vault_file):
    add_webhook(vault_file, "slack", "https://hooks.slack.com/abc")
    hooks = list_webhooks(vault_file)
    assert set(hooks["slack"]["events"]) == {"set", "delete", "rotate"}


def test_add_webhook_custom_events(vault_file):
    add_webhook(vault_file, "ci", "https://example.com", events=["rotate"])
    assert get_webhook(vault_file, "ci")["events"] == ["rotate"]


def test_add_webhook_empty_name_raises(vault_file):
    with pytest.raises(WebhookError):
        add_webhook(vault_file, "", "https://example.com")


def test_add_webhook_empty_url_raises(vault_file):
    with pytest.raises(WebhookError):
        add_webhook(vault_file, "slack", "")


def test_remove_webhook_success(vault_file):
    add_webhook(vault_file, "slack", "https://hooks.slack.com/abc")
    remove_webhook(vault_file, "slack")
    assert "slack" not in list_webhooks(vault_file)


def test_remove_webhook_not_found_raises(vault_file):
    with pytest.raises(WebhookError):
        remove_webhook(vault_file, "nonexistent")


def test_get_webhook_not_found_raises(vault_file):
    with pytest.raises(WebhookError):
        get_webhook(vault_file, "missing")


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_webhook_add_success(runner, vault_file):
    result = runner.invoke(webhook_group, ["add", "slack", "https://example.com", "--vault", vault_file])
    assert result.exit_code == 0
    assert "slack" in result.output


def test_cli_webhook_list_empty(runner, vault_file):
    result = runner.invoke(webhook_group, ["list", "--vault", vault_file])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_cli_webhook_remove_not_found(runner, vault_file):
    result = runner.invoke(webhook_group, ["remove", "ghost", "--vault", vault_file])
    assert result.exit_code == 1
