"""Variable quality rating/scoring for envault."""
import json
from pathlib import Path

RATING_FILENAME = ".envault_ratings.json"
VALID_RATINGS = {1, 2, 3, 4, 5}


class RatingError(Exception):
    pass


def _rating_path(vault_path: str) -> Path:
    return Path(vault_path).parent / RATING_FILENAME


def _load_ratings(vault_path: str) -> dict:
    p = _rating_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_ratings(vault_path: str, data: dict) -> None:
    p = _rating_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def set_rating(vault_path: str, key: str, rating: int) -> None:
    if rating not in VALID_RATINGS:
        raise RatingError(f"Rating must be between 1 and 5, got {rating}")
    data = _load_ratings(vault_path)
    data[key] = rating
    _save_ratings(vault_path, data)


def get_rating(vault_path: str, key: str) -> int | None:
    return _load_ratings(vault_path).get(key)


def remove_rating(vault_path: str, key: str) -> None:
    data = _load_ratings(vault_path)
    if key not in data:
        raise RatingError(f"No rating found for '{key}'")
    del data[key]
    _save_ratings(vault_path, data)


def list_ratings(vault_path: str) -> dict:
    return _load_ratings(vault_path)
