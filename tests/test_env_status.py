"""Tests for envault/env_status.py"""

import os
import json
import pytest
import datetime
from unittest.mock import patch
from envault.env_status import StatusReport, get_status


@pytest.fixture
def vault_file(tmp_path, monkeypatch):
    from envault.vault import init_vault, set_variable
    vf = str(tmp_path / "test.vault")
    init_vault(vf, "password")
    set_variable(vf, "password", "KEY1", "val1")
    set_variable(vf, "password", "KEY2", "val2")
    monkeypatch.chdir(tmp_path)
    return vf


def test_status_report_defaults():
    r = StatusReport(vault_path="x.vault")
    assert r.total_keys == 0
    assert r.has_issues() is False


def test_status_report_has_issues_when_expiring():
    r = StatusReport(vault_path="x.vault", expiring_keys=["OLD_KEY"])
    assert r.has_issues() is True


def test_get_status_total_keys(vault_file, tmp_path):
    with patch("envault.env_status.get_locked", return_value=set()), \
         patch("envault.env_status.list_pinned", return_value=set()), \
         patch("envault.env_status.list_sensitive", return_value=set()), \
         patch("envault.env_status.list_readonly", return_value=set()), \
         patch("envault.env_status.list_required", return_value=set()), \
         patch("envault.env_status.list_expiring", return_value={}):
        report = get_status(vault_file, "password")
    assert report.total_keys == 2


def test_get_status_locked_keys(vault_file, tmp_path):
    with patch("envault.env_status.get_locked", return_value={"KEY1"}), \
         patch("envault.env_status.list_pinned", return_value=set()), \
         patch("envault.env_status.list_sensitive", return_value=set()), \
         patch("envault.env_status.list_readonly", return_value=set()), \
         patch("envault.env_status.list_required", return_value=set()), \
         patch("envault.env_status.list_expiring", return_value={}):
        report = get_status(vault_file, "password")
    assert "KEY1" in report.locked_keys


def test_get_status_expired_keys(vault_file):
    past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    with patch("envault.env_status.get_locked", return_value=set()), \
         patch("envault.env_status.list_pinned", return_value=set()), \
         patch("envault.env_status.list_sensitive", return_value=set()), \
         patch("envault.env_status.list_readonly", return_value=set()), \
         patch("envault.env_status.list_required", return_value=set()), \
         patch("envault.env_status.list_expiring", return_value={"KEY2": past}):
        report = get_status(vault_file, "password")
    assert "KEY2" in report.expiring_keys
    assert report.has_issues() is True
