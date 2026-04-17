"""Integration tests: visibility group registered on main CLI."""

import json
import pytest
from click.testing import CliRunner
import click
from envault.cli_visibility import visibility_group


def _make_main_cli():
    @click.group()
    def main():
        pass
    main.add_command(visibility_group)
    return main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_file(tmp_path):
    vf = tmp_path / ".envault"
    vf.write_text(json.dumps({"salt": "abc", "variables": {}}))
    return str(vf)


def test_main_cli_has_visibility_command(runner):
    main = _make_main_cli()
    result = runner.invoke(main, ["--help"])
    assert "visibility" in result.output


def test_visibility_set_and_list_roundtrip(runner, vault_file):
    main = _make_main_cli()
    runner.invoke(main, ["visibility", "set", "MY_VAR", "secret", "--vault", vault_file])
    result = runner.invoke(main, ["visibility", "list", "--vault", vault_file])
    assert "MY_VAR" in result.output
    assert "secret" in result.output


def test_visibility_subcommands_present(runner):
    main = _make_main_cli()
    result = runner.invoke(main, ["visibility", "--help"])
    for cmd in ("set", "get", "remove", "list", "filter"):
        assert cmd in result.output
