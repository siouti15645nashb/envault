"""Integration test: compare group registered on main CLI."""
import pytest
from click.testing import CliRunner
from click import Group
import click
from envault.cli import cli
from envault.cli_compare import compare_group
from envault.vault import init_vault, set_variable

PASSWORD = "pass"


@pytest.fixture
def main_cli():
    @click.group()
    def _cli():
        pass
    _cli.add_command(compare_group)
    return _cli


@pytest.fixture
def runner():
    return CliRunner()


def test_compare_group_has_run_command():
    assert "run" in compare_group.commands


def test_compare_run_via_group(runner, tmp_path, main_cli):
    a = str(tmp_path / "a.vault")
    b = str(tmp_path / "b.vault")
    init_vault(a, PASSWORD)
    init_vault(b, PASSWORD)
    result = runner.invoke(main_cli, ["compare", "run", a, b, "--password-a", PASSWORD, "--password-b", PASSWORD])
    assert "identical" in result.output
    assert result.exit_code == 0
