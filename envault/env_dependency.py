import json
from pathlib import Path

DEPENDENCY_FILENAME = ".envault_dependencies.json"


class DependencyError(Exception):
    pass


def _dependency_path(vault_path: str) -> Path:
    return Path(vault_path).parent / DEPENDENCY_FILENAME


def _load_dependencies(vault_path: str) -> dict:
    p = _dependency_path(vault_path)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_dependencies(vault_path: str, data: dict) -> None:
    p = _dependency_path(vault_path)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def add_dependency(vault_path: str, key: str, depends_on: str) -> None:
    """Record that `key` depends on `depends_on`."""
    if key == depends_on:
        raise DependencyError("A variable cannot depend on itself.")
    data = _load_dependencies(vault_path)
    deps = set(data.get(key, []))
    deps.add(depends_on)
    data[key] = sorted(deps)
    _save_dependencies(vault_path, data)


def remove_dependency(vault_path: str, key: str, depends_on: str) -> None:
    data = _load_dependencies(vault_path)
    deps = set(data.get(key, []))
    deps.discard(depends_on)
    if deps:
        data[key] = sorted(deps)
    else:
        data.pop(key, None)
    _save_dependencies(vault_path, data)


def get_dependencies(vault_path: str, key: str) -> list:
    data = _load_dependencies(vault_path)
    return data.get(key, [])


def list_all_dependencies(vault_path: str) -> dict:
    return _load_dependencies(vault_path)


def check_missing(vault_path: str, available_keys: list) -> dict:
    """Return a mapping of key -> [missing deps] for any unresolved dependencies."""
    data = _load_dependencies(vault_path)
    available = set(available_keys)
    missing = {}
    for key, deps in data.items():
        absent = [d for d in deps if d not in available]
        if absent:
            missing[key] = absent
    return missing
