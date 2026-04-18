"""Tests for envault.env_rating."""
import pytest
from click.testing import CliRunner
from envault.vault import init_vault, set_variable
from envault.env_rating import (
    RATING_FILENAME,
    RatingError,
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
    _rating_path,
)
from envault.cli_rating import rating_group


@pytest.fixture
def vault_file(tmp_path):
    vf = str(tmp_path / ".envault")
    init_vault(vf, "password")
    set_variable(vf, "password", "API_KEY", "abc123")
    return vf


def test_rating_filename_constant():
    assert RATING_FILENAME == ".envault_ratings.json"


def test_rating_path_returns_correct_path(vault_file, tmp_path):
    p = _rating_path(vault_file)
    assert p.name == RATING_FILENAME
    assert p.parent == tmp_path


def test_list_ratings_empty_when_no_file(vault_file):
    assert list_ratings(vault_file) == {}


def test_set_rating_creates_file(vault_file, tmp_path):
    set_rating(vault_file, "API_KEY", 4)
    assert (tmp_path / RATING_FILENAME).exists()


def test_set_rating_stores_value(vault_file):
    set_rating(vault_file, "API_KEY", 3)
    assert get_rating(vault_file, "API_KEY") == 3


def test_set_rating_invalid_raises(vault_file):
    with pytest.raises(RatingError):
        set_rating(vault_file, "API_KEY", 0)
    with pytest.raises(RatingError):
        set_rating(vault_file, "API_KEY", 6)


def test_get_rating_none_when_not_set(vault_file):
    assert get_rating(vault_file, "MISSING") is None


def test_remove_rating_success(vault_file):
    set_rating(vault_file, "API_KEY", 5)
    remove_rating(vault_file, "API_KEY")
    assert get_rating(vault_file, "API_KEY") is None


def test_remove_rating_missing_raises(vault_file):
    with pytest.raises(RatingError):
        remove_rating(vault_file, "NONEXISTENT")


def test_list_ratings_returns_all(vault_file):
    set_rating(vault_file, "API_KEY", 2)
    set_rating(vault_file, "DB_URL", 5)
    result = list_ratings(vault_file)
    assert result["API_KEY"] == 2
    assert result["DB_URL"] == 5


def test_cli_set_and_get(vault_file):
    runner = CliRunner()
    result = runner.invoke(rating_group, ["set", "API_KEY", "4", "--vault", vault_file])
    assert result.exit_code == 0
    assert "set to 4" in result.output
    result = runner.invoke(rating_group, ["get", "API_KEY", "--vault", vault_file])
    assert "4/5" in result.output


def test_cli_list_empty(vault_file):
    runner = CliRunner()
    result = runner.invoke(rating_group, ["list", "--vault", vault_file])
    assert "No ratings" in result.output


def test_cli_set_invalid_rating(vault_file):
    runner = CliRunner()
    result = runner.invoke(rating_group, ["set", "API_KEY", "9", "--vault", vault_file])
    assert result.exit_code == 1
