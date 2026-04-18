"""Tests for envault/cli_status.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_status import status_group
from envault.env_status import StatusReport


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    from envault.vault import init_vault, set_variable
    vf = str(tmp_path / "test.vault")
    init_vault(vf, "password")
    set_variable(vf, "password", "FOO", "bar")
    return vf


def _mock_report(**kwargs):
    defaults = dict(
        vault_path="x.vault", total_keys=1,
        locked_keys=[], pinned_keys=[], sensitive_keys=[],
        expiring_keys=[], readonly_keys=[], required_keys=[]
    )
    defaults.update(kwargs)
    return StatusReport(**defaults)


def test_status_show_success(runner, vault_file):
    with patch("envault.cli_status.get_status", return_value=_mock_report(total_keys=1)):
        result = runner.invoke(status_group, ["show", vault_file, "--password", "password"])
    assert result.exit_code == 0
    assert "Total keys" in result.output


def test_status_show_no_issues(runner, vault_file):
    with patch("envault.cli_status.get_status", return_value=_mock_report()):
        result = runner.invoke(status_group, ["show", vault_file, "--password", "password"])
    assert "none" in result.output


def test_status_show_expiring(runner, vault_file):
    with patch("envault.cli_status.get_status",
               return_value=_mock_report(expiring_keys=["OLD"])):
        result = runner.invoke(status_group, ["show", vault_file, "--password", "password"])
    assert "OLD" in result.output


def test_status_issues_exit_zero_when_clean(runner, vault_file):
    with patch("envault.cli_status.get_status", return_value=_mock_report()):
        result = runner.invoke(status_group, ["issues", vault_file, "--password", "password"])
    assert result.exit_code == 0
    assert "No issues" in result.output


def test_status_issues_exit_nonzero_when_expired(runner, vault_file):
    with patch("envault.cli_status.get_status",
               return_value=_mock_report(expiring_keys=["STALE"])):
        result = runner.invoke(status_group, ["issues", vault_file, "--password", "password"])
    assert result.exit_code != 0
    assert "STALE" in result.output


def test_status_show_error_handling(runner):
    with patch("envault.cli_status.get_status", side_effect=Exception("vault missing")):
        result = runner.invoke(status_group, ["show", "missing.vault", "--password", "x"])
    assert result.exit_code != 0
    assert "vault missing" in result.output
