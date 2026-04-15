"""Tests for envault/templates.py"""

import json
import pytest
from pathlib import Path
from envault.templates import (
    TEMPLATES_FILENAME,
    TemplateError,
    save_template,
    delete_template,
    get_template,
    list_templates,
    apply_template,
)


@pytest.fixture
def tmpdir_str(tmp_path):
    return str(tmp_path)


def test_templates_filename_constant():
    assert TEMPLATES_FILENAME == ".envault_templates.json"


def test_save_template_creates_file(tmpdir_str):
    save_template("backend", ["DB_URL", "SECRET_KEY"], directory=tmpdir_str)
    path = Path(tmpdir_str) / TEMPLATES_FILENAME
    assert path.exists()


def test_save_template_stores_keys(tmpdir_str):
    save_template("frontend", ["API_URL", "APP_PORT"], directory=tmpdir_str)
    data = json.loads((Path(tmpdir_str) / TEMPLATES_FILENAME).read_text())
    assert data["frontend"] == ["API_URL", "APP_PORT"]


def test_save_template_empty_name_raises(tmpdir_str):
    with pytest.raises(TemplateError, match="empty"):
        save_template("", ["KEY"], directory=tmpdir_str)


def test_save_template_empty_keys_raises(tmpdir_str):
    with pytest.raises(TemplateError, match="at least one key"):
        save_template("empty", [], directory=tmpdir_str)


def test_get_template_returns_keys(tmpdir_str):
    save_template("svc", ["HOST", "PORT"], directory=tmpdir_str)
    keys = get_template("svc", directory=tmpdir_str)
    assert keys == ["HOST", "PORT"]


def test_get_template_nonexistent_raises(tmpdir_str):
    with pytest.raises(TemplateError, match="does not exist"):
        get_template("ghost", directory=tmpdir_str)


def test_delete_template_removes_entry(tmpdir_str):
    save_template("tmp", ["X"], directory=tmpdir_str)
    delete_template("tmp", directory=tmpdir_str)
    assert "tmp" not in list_templates(directory=tmpdir_str)


def test_delete_template_nonexistent_raises(tmpdir_str):
    with pytest.raises(TemplateError, match="does not exist"):
        delete_template("nope", directory=tmpdir_str)


def test_list_templates_empty(tmpdir_str):
    assert list_templates(directory=tmpdir_str) == {}


def test_list_templates_returns_all(tmpdir_str):
    save_template("a", ["K1"], directory=tmpdir_str)
    save_template("b", ["K2", "K3"], directory=tmpdir_str)
    result = list_templates(directory=tmpdir_str)
    assert set(result.keys()) == {"a", "b"}


def test_apply_template_all_present(tmpdir_str):
    save_template("full", ["A", "B"], directory=tmpdir_str)
    result = apply_template("full", ["A", "B", "C"], directory=tmpdir_str)
    assert result == {"A": True, "B": True}


def test_apply_template_partial_missing(tmpdir_str):
    save_template("partial", ["A", "B", "D"], directory=tmpdir_str)
    result = apply_template("partial", ["A", "C"], directory=tmpdir_str)
    assert result["A"] is True
    assert result["B"] is False
    assert result["D"] is False


def test_apply_template_nonexistent_raises(tmpdir_str):
    with pytest.raises(TemplateError):
        apply_template("missing", ["X"], directory=tmpdir_str)
