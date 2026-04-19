import pytest
import json
from pathlib import Path
from envault.env_region import (
    REGION_FILENAME, VALID_REGIONS,
    set_region, get_region, remove_region, list_regions,
    RegionError, _region_path
)


@pytest.fixture
def vault_dir(tmp_path):
    from envault.vault import init_vault
    init_vault(str(tmp_path), "password")
    return str(tmp_path)


def test_region_filename_constant():
    assert REGION_FILENAME == ".envault_regions.json"


def test_valid_regions_includes_common():
    assert "us-east-1" in VALID_REGIONS
    assert "eu-west-1" in VALID_REGIONS
    assert "global" in VALID_REGIONS


def test_region_path_returns_correct_path(vault_dir):
    p = _region_path(vault_dir)
    assert p.name == REGION_FILENAME
    assert p.parent == Path(vault_dir)


def test_list_regions_empty_when_no_file(vault_dir):
    assert list_regions(vault_dir) == {}


def test_set_region_creates_file(vault_dir):
    set_region(vault_dir, "API_URL", "us-east-1")
    assert _region_path(vault_dir).exists()


def test_set_region_stores_value(vault_dir):
    set_region(vault_dir, "API_URL", "eu-central-1")
    assert get_region(vault_dir, "API_URL") == "eu-central-1"


def test_get_region_returns_none_when_not_set(vault_dir):
    assert get_region(vault_dir, "MISSING") is None


def test_set_region_invalid_raises(vault_dir):
    with pytest.raises(RegionError):
        set_region(vault_dir, "KEY", "mars-north-1")


def test_remove_region_success(vault_dir):
    set_region(vault_dir, "DB_HOST", "ap-northeast-1")
    remove_region(vault_dir, "DB_HOST")
    assert get_region(vault_dir, "DB_HOST") is None


def test_remove_region_not_set_raises(vault_dir):
    with pytest.raises(RegionError):
        remove_region(vault_dir, "NONEXISTENT")


def test_list_regions_returns_all(vault_dir):
    set_region(vault_dir, "A", "us-east-1")
    set_region(vault_dir, "B", "eu-west-1")
    result = list_regions(vault_dir)
    assert result["A"] == "us-east-1"
    assert result["B"] == "eu-west-1"


def test_set_region_overwrites(vault_dir):
    set_region(vault_dir, "KEY", "us-east-1")
    set_region(vault_dir, "KEY", "global")
    assert get_region(vault_dir, "KEY") == "global"
