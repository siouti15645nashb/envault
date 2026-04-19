import os
import pytest
from click.testing import CliRunner
from envault.env_approval import (
    APPROVAL_FILENAME,
    ApprovalError,
    request_approval,
    review_approval,
    get_approval,
    list_approvals,
    remove_approval,
)
from envault.cli_approval import approval_group


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return Runner()


class Runner:
    def __init__(self):
        self._runner = CliRunner()

    def invoke(self, *args, **kwargs):
        return self._runner.invoke(*args, **kwargs)


def test_approval_filename_constant():
    assert APPROVAL_FILENAME == ".envault_approvals.json"


def test_list_approvals_empty_when_no_file(vault_dir):
    assert list_approvals(vault_dir) == {}


def test_request_approval_creates_file(vault_dir):
    request_approval(vault_dir, "MY_KEY", "alice")
    assert os.path.exists(os.path.join(vault_dir, APPROVAL_FILENAME))


def test_request_approval_stores_pending(vault_dir):
    entry = request_approval(vault_dir, "MY_KEY", "alice")
    assert entry["status"] == "pending"
    assert entry["requester"] == "alice"
    assert entry["reviewed_by"] is None


def test_get_approval_returns_entry(vault_dir):
    request_approval(vault_dir, "MY_KEY", "alice")
    entry = get_approval(vault_dir, "MY_KEY")
    assert entry is not None
    assert entry["requester"] == "alice"


def test_get_approval_returns_none_for_missing(vault_dir):
    assert get_approval(vault_dir, "MISSING") is None


def test_review_approval_sets_status(vault_dir):
    request_approval(vault_dir, "MY_KEY", "alice")
    entry = review_approval(vault_dir, "MY_KEY", "bob", "approved")
    assert entry["status"] == "approved"
    assert entry["reviewed_by"] == "bob"


def test_review_approval_rejected(vault_dir):
    request_approval(vault_dir, "MY_KEY", "alice")
    entry = review_approval(vault_dir, "MY_KEY", "bob", "rejected")
    assert entry["status"] == "rejected"


def test_review_approval_invalid_status_raises(vault_dir):
    request_approval(vault_dir, "MY_KEY", "alice")
    with pytest.raises(ApprovalError):
        review_approval(vault_dir, "MY_KEY", "bob", "unknown")


def test_review_approval_missing_key_raises(vault_dir):
    with pytest.raises(ApprovalError):
        review_approval(vault_dir, "MISSING", "bob", "approved")


def test_list_approvals_filter_by_status(vault_dir):
    request_approval(vault_dir, "KEY_A", "alice")
    request_approval(vault_dir, "KEY_B", "bob")
    review_approval(vault_dir, "KEY_A", "carol", "approved")
    pending = list_approvals(vault_dir, status="pending")
    assert "KEY_B" in pending
    assert "KEY_A" not in pending


def test_remove_approval_deletes_entry(vault_dir):
    request_approval(vault_dir, "MY_KEY", "alice")
    remove_approval(vault_dir, "MY_KEY")
    assert get_approval(vault_dir, "MY_KEY") is None


def test_remove_approval_missing_raises(vault_dir):
    with pytest.raises(ApprovalError):
        remove_approval(vault_dir, "MISSING")


def test_cli_request_success(vault_dir):
    r = CliRunner()
    result = r.invoke(approval_group, ["request", "MY_KEY", "alice", vault_dir])
    assert result.exit_code == 0
    assert "pending" in result.output


def test_cli_review_success(vault_dir):
    r = CliRunner()
    request_approval(vault_dir, "MY_KEY", "alice")
    result = r.invoke(approval_group, ["review", "MY_KEY", "bob", "approved", vault_dir])
    assert result.exit_code == 0
    assert "approved" in result.output


def test_cli_list_shows_entries(vault_dir):
    r = CliRunner()
    request_approval(vault_dir, "MY_KEY", "alice")
    result = r.invoke(approval_group, ["list", vault_dir])
    assert "MY_KEY" in result.output
