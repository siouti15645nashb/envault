import os
import pytest
from click.testing import CliRunner
from envault.env_masking import (
    MASKING_FILENAME,
    enable_masking,
    disable_masking,
    is_masked,
    mask_value,
    get_display_value,
    list_masked,
)
from envault.cli_masking import masking_group


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def test_masking_filename_constant():
    assert MASKING_FILENAME == ".envault_masking.json"


def test_list_masked_empty_when_no_file(vault_dir):
    assert list_masked(vault_dir) == []


def test_is_masked_false_when_no_file(vault_dir):
    assert is_masked(vault_dir, "MY_KEY") is False


def test_enable_masking_creates_file(vault_dir):
    enable_masking(vault_dir, "SECRET")
    assert os.path.exists(os.path.join(vault_dir, MASKING_FILENAME))


def test_is_masked_true_after_enable(vault_dir):
    enable_masking(vault_dir, "SECRET")
    assert is_masked(vault_dir, "SECRET") is True


def test_is_masked_false_after_disable(vault_dir):
    enable_masking(vault_dir, "SECRET")
    disable_masking(vault_dir, "SECRET")
    assert is_masked(vault_dir, "SECRET") is False


def test_list_masked_returns_keys(vault_dir):
    enable_masking(vault_dir, "KEY_A")
    enable_masking(vault_dir, "KEY_B")
    result = list_masked(vault_dir)
    assert set(result) == {"KEY_A", "KEY_B"}


def test_mask_value_hides_end(vault_dir):
    result = mask_value("mysecret", visible_chars=2)
    assert result == "my******"


def test_mask_value_short_string():
    result = mask_value("ab", visible_chars=4)
    assert result == "**"


def test_get_display_value_masked(vault_dir):
    enable_masking(vault_dir, "TOKEN", visible_chars=3)
    result = get_display_value(vault_dir, "TOKEN", "abcdefgh")
    assert result == "abc*****"


def test_get_display_value_unmasked(vault_dir):
    result = get_display_value(vault_dir, "TOKEN", "abcdefgh")
    assert result == "abcdefgh"


def test_cli_mask_enable(runner, vault_dir):
    result = runner.invoke(masking_group, ["enable", "MY_KEY", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "MY_KEY" in result.output


def test_cli_mask_list_empty(runner, vault_dir):
    result = runner.invoke(masking_group, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "No masked" in result.output


def test_cli_mask_list_shows_key(runner, vault_dir):
    enable_masking(vault_dir, "DB_PASS")
    result = runner.invoke(masking_group, ["list", "--vault-dir", vault_dir])
    assert "DB_PASS" in result.output


def test_cli_mask_check_masked(runner, vault_dir):
    enable_masking(vault_dir, "API_KEY")
    result = runner.invoke(masking_group, ["check", "API_KEY", "--vault-dir", vault_dir])
    assert "masked" in result.output
