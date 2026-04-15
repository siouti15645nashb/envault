"""Main CLI entry point for envault."""

import click

from envault.vault import (
    init_vault,
    set_variable,
    get_variable,
    list_variables,
    VaultError,
)
from envault.cli_audit import audit_group
from envault.cli_search import search_group
from envault.cli_diff import diff_group


@click.group()
def cli():
    """envault — encrypted project environment variable manager."""


@cli.command(name="init")
@click.argument("vault_path")
@click.password_option(help="Master password for the vault.")
def cmd_init(vault_path, password):
    """Initialise a new vault at VAULT_PATH."""
    try:
        init_vault(vault_path, password)
        click.echo(f"Vault initialised at {vault_path}")
    except VaultError as exc:
        raise click.ClickException(str(exc))


@cli.command(name="set")
@click.argument("vault_path")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", "-p", prompt="Vault password",
                       confirmation_prompt=False)
def cmd_set(vault_path, key, value, password):
    """Set KEY=VALUE in the vault at VAULT_PATH."""
    try:
        set_variable(vault_path, password, key, value)
        click.echo(f"Set {key}")
    except VaultError as exc:
        raise click.ClickException(str(exc))


@cli.command(name="get")
@click.argument("vault_path")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password",
                       confirmation_prompt=False)
def cmd_get(vault_path, key, password):
    """Get the value of KEY from the vault at VAULT_PATH."""
    try:
        value = get_variable(vault_path, password, key)
        click.echo(value)
    except VaultError as exc:
        raise click.ClickException(str(exc))


@cli.command(name="list")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt="Vault password",
                       confirmation_prompt=False)
def cmd_list(vault_path, password):
    """List all keys stored in the vault at VAULT_PATH."""
    try:
        variables = list_variables(vault_path, password)
        if not variables:
            click.echo("(empty vault)")
        else:
            for key in sorted(variables):
                click.echo(key)
    except VaultError as exc:
        raise click.ClickException(str(exc))


cli.add_command(audit_group)
cli.add_command(search_group)
cli.add_command(diff_group)


if __name__ == "__main__":
    cli()
