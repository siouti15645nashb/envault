"""Main CLI entry point for envault."""

import click
from envault.vault import VaultError, init_vault, set_variable, get_variable, list_variables
from envault.cli_audit import audit_group
from envault.cli_search import search_group
from envault.cli_diff import diff_group
from envault.cli_backup import backup_group
from envault.cli_history import history_group
from envault.cli_tags import tags_group

DEFAULT_VAULT = ".envault"


@click.group()
def cli():
    """envault — encrypted project environment variable manager."""


@cli.command(name="init")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Master password")
def cmd_init(vault, password):
    """Initialise a new vault."""
    try:
        init_vault(vault, password)
        click.echo(f"Vault initialised at '{vault}'.")
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_set(key, value, vault, password):
    """Set an environment variable."""
    try:
        set_variable(vault, password, key, value)
        click.echo(f"Set '{key}'.")
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command(name="get")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_get(key, vault, password):
    """Get an environment variable."""
    try:
        value = get_variable(vault, password, key)
        click.echo(value)
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command(name="list")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
@click.password_option(prompt="Master password", confirmation_prompt=False)
def cmd_list(vault, password):
    """List all variable keys."""
    try:
        keys = list_variables(vault, password)
        if keys:
            for key in keys:
                click.echo(key)
        else:
            click.echo("No variables set.")
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


cli.add_command(audit_group)
cli.add_command(search_group)
cli.add_command(diff_group)
cli.add_command(backup_group)
cli.add_command(history_group)
cli.add_command(tags_group)

if __name__ == "__main__":
    cli()
