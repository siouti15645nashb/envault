"""Tests for envault.env_watch module."""

import os
import json
import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable, delete_variable
from envault.env_watch import watch_vault, WatchError, _file_hash


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    return path


def test_file_hash_returns_string(vault_file):
    h = _file_hash(vault_file)
    assert isinstance(h, str)
    assert len(h) == 32


def test_file_hash_none_for_missing():
    assert _file_hash("/nonexistent/path/.envault") is None


def test_file_hash_changes_after_write(vault_file):
    h1 = _file_hash(vault_file)
    set_variable(vault_file, "secret", "KEY", "value")
    h2 = _file_hash(vault_file)
    assert h1 != h2


def test_watch_raises_if_no_vault(tmp_path):
    path = str(tmp_path / ".envault")
    with pytest.raises(WatchError):
        watch_vault(path, "secret", lambda *a: None, max_iterations=1)


def test_watch_detects_added_key(vault_file):
    events = []

    def on_change(path, added, removed):
        events.append((added, removed))

    import threading

    def modify():
        import time
        time.sleep(0.05)
        set_variable(vault_file, "secret", "NEW_KEY", "hello")

    t = threading.Thread(target=modify)
    t.start()
    watch_vault(vault_file, "secret", on_change, interval=0.02, max_iterations=20)
    t.join()

    assert any("NEW_KEY" in added for added, _ in events)


def test_watch_detects_removed_key(vault_file):
    set_variable(vault_file, "secret", "OLD_KEY", "val")
    events = []

    def on_change(path, added, removed):
        events.append((added, removed))

    import threading

    def modify():
        import time
        time.sleep(0.05)
        delete_variable(vault_file, "secret", "OLD_KEY")

    t = threading.Thread(target=modify)
    t.start()
    watch_vault(vault_file, "secret", on_change, interval=0.02, max_iterations=20)
    t.join()

    assert any("OLD_KEY" in removed for _, removed in events)
