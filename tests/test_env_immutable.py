import json
import pytest
from pathlib import Path
from envault.env_immutable import (
    IMMUTABLE_FILENAME,
    ImmutableError,
    _immutable_path,
    mark_immutable,
    unmark_immutable,
    is_immutable,
    list_immutable,
)
from envault.vault import init_vault


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "vault.json")
    init_vault(path, "password")
    return path


def test_immutable_filename_constant():
    assert IMMUTABLE_FILENAME == ".envault_immutable.json"


def test_immutable_path_returns_correct_path(vault_file):
    p = _immutable_path(vault_file)
    assert p.name == IMMUTABLE_FILENAME
    assert p.parent == Path(vault_file).parent


def test_list_immutable_empty_when_no_file(vault_file):
    assert list_immutable(vault_file) == []


def test_is_immutable_false_when_no_file(vault_file):
    assert is_immutable(vault_file, "MY_KEY") is False


def test_mark_immutable_creates_file(vault_file):
    mark_immutable(vault_file, "MY_KEY")
    p = _immutable_path(vault_file)
    assert p.exists()


def test_mark_immutable_key_appears_in_list(vault_file):
    mark_immutable(vault_file, "MY_KEY")
    assert "MY_KEY" in list_immutable(vault_file)


def test_mark_immutable_idempotent(vault_file):
    mark_immutable(vault_file, "MY_KEY")
    mark_immutable(vault_file, "MY_KEY")
    assert list_immutable(vault_file).count("MY_KEY") == 1


def test_is_immutable_true_after_mark(vault_file):
    mark_immutable(vault_file, "MY_KEY")
    assert is_immutable(vault_file, "MY_KEY") is True


def test_unmark_immutable_removes_key(vault_file):
    mark_immutable(vault_file, "MY_KEY")
    unmark_immutable(vault_file, "MY_KEY")
    assert is_immutable(vault_file, "MY_KEY") is False


def test_unmark_immutable_raises_if_not_marked(vault_file):
    with pytest.raises(ImmutableError):
        unmark_immutable(vault_file, "GHOST_KEY")


def test_list_immutable_sorted(vault_file):
    mark_immutable(vault_file, "Z_KEY")
    mark_immutable(vault_file, "A_KEY")
    result = list_immutable(vault_file)
    assert result == sorted(result)
