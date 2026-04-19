import json
from pathlib import Path

REGION_FILENAME = ".envault_regions.json"

VALID_REGIONS = [
    "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
    "ap-southeast-1", "ap-northeast-1", "sa-east-1", "global"
]


class RegionError(Exception):
    pass


def _region_path(vault_dir: str) -> Path:
    return Path(vault_dir) / REGION_FILENAME


def _load_regions(vault_dir: str) -> dict:
    path = _region_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_regions(vault_dir: str, data: dict) -> None:
    path = _region_path(vault_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_region(vault_dir: str, key: str, region: str) -> None:
    if region not in VALID_REGIONS:
        raise RegionError(f"Invalid region '{region}'. Valid: {VALID_REGIONS}")
    data = _load_regions(vault_dir)
    data[key] = region
    _save_regions(vault_dir, data)


def get_region(vault_dir: str, key: str) -> str | None:
    return _load_regions(vault_dir).get(key)


def remove_region(vault_dir: str, key: str) -> None:
    data = _load_regions(vault_dir)
    if key not in data:
        raise RegionError(f"No region set for '{key}'")
    del data[key]
    _save_regions(vault_dir, data)


def list_regions(vault_dir: str) -> dict:
    return _load_regions(vault_dir)
