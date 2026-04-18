import pytest
from click.testing import CliRunner
from click import group
from envault.cli_severity import severity_group
from envault.env_severity import set_severity


def _make_main_cli():
    @group()
    def main():
        pass
    main.add_command(severity_group)
    return main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def main_cli():
    return _make_main_cli()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_main_cli_has_severity_command(runner, main_cli):
    result = runner.invoke(main_cli, ["--help"])
    assert "severity" in result.output


def test_severity_set_and_list_roundtrip(runner, main_cli, vault_dir):
    runner.invoke(main_cli, ["severity", "set", "MY_VAR", "high", "--vault-dir", vault_dir])
    result = runner.invoke(main_cli, ["severity", "list", "--vault-dir", vault_dir])
    assert "MY_VAR" in result.output
    assert "high" in result.output


def test_severity_find_via_main(runner, main_cli, vault_dir):
    set_severity(vault_dir, "CRIT_VAR", "critical")
    result = runner.invoke(main_cli, ["severity", "find", "critical", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "CRIT_VAR" in result.output
