"""Tests for envault.cli_watch module."""

import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.cli_watch import watch_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / ".envault")
    init_vault(path, "secret")
    return path


def test_watch_start_missing_vault(runner, tmp_path):
    path = str(tmp_path / ".envault")
    result = runner.invoke(
        watch_group,
        ["start", path, "--password", "secret", "--interval", "0.01"],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_watch_start_prints_watching(runner, vault_file, monkeypatch):
    """Patch watch_vault to avoid blocking; verify output prefix."""
    import envault.cli_watch as cw

    monkeypatch.setattr(
        cw,
        "watch_vault",
        lambda *a, **kw: None,
    )
    result = runner.invoke(
        watch_group,
        ["start", vault_file, "--password", "secret"],
    )
    assert result.exit_code == 0
    assert "Watching" in result.output


def test_watch_start_shows_added_key(runner, vault_file, monkeypatch):
    import envault.cli_watch as cw

    captured = {}

    def fake_watch(path, password, on_change, interval=1.0, max_iterations=None):
        on_change(path, {"MY_KEY"}, set())

    monkeypatch.setattr(cw, "watch_vault", fake_watch)
    result = runner.invoke(
        watch_group,
        ["start", vault_file, "--password", "secret"],
    )
    assert "[+] Added:   MY_KEY" in result.output


def test_watch_start_shows_removed_key(runner, vault_file, monkeypatch):
    import envault.cli_watch as cw

    def fake_watch(path, password, on_change, interval=1.0, max_iterations=None):
        on_change(path, set(), {"OLD_KEY"})

    monkeypatch.setattr(cw, "watch_vault", fake_watch)
    result = runner.invoke(
        watch_group,
        ["start", vault_file, "--password", "secret"],
    )
    assert "[-] Removed: OLD_KEY" in result.output
