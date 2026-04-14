"""CLI entry point for envault."""

import sys
from pathlib import Path

import click

from envault.vault import (
    init_vault,
    set_variable,
    get_variable,
    list_variables,
    VaultExistsError,
    VaultNotFoundError,
)
from envault.export import export_variables, SUPPORTED_FORMATS

DEFAULT_VAULT = Path(".envault")


@click.group()
def cli():
    """envault — encrypted environment variable manager."""


@cli.command("init")
@click.password_option(prompt="Master password", help="Master password for the vault.")
def cmd_init(password):
    """Initialise a new vault in the current directory."""
    try:
        init_vault(DEFAULT_VAULT, password)
        click.echo("Vault initialised successfully.")
    except VaultExistsError:
        click.echo("Error: vault already exists.", err=True)
        sys.exit(1)


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Master password", help="Master password for the vault.")
def cmd_set(key, value, password):
    """Store an encrypted variable in the vault."""
    try:
        set_variable(DEFAULT_VAULT, password, key, value)
        click.echo(f"Variable '{key}' stored.")
    except VaultNotFoundError:
        click.echo("Error: vault not found. Run 'envault init' first.", err=True)
        sys.exit(1)


@cli.command("get")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
def cmd_get(key, password):
    """Retrieve and print a variable from the vault."""
    try:
        value = get_variable(DEFAULT_VAULT, password, key)
        click.echo(value)
    except VaultNotFoundError:
        click.echo("Error: vault not found.", err=True)
        sys.exit(1)
    except KeyError:
        click.echo(f"Error: key '{key}' not found.", err=True)
        sys.exit(1)


@cli.command("list")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
def cmd_list(password):
    """List all variable names stored in the vault."""
    try:
        keys = list_variables(DEFAULT_VAULT, password)
        if not keys:
            click.echo("No variables stored.")
        else:
            for key in keys:
                click.echo(key)
    except VaultNotFoundError:
        click.echo("Error: vault not found.", err=True)
        sys.exit(1)


@cli.command("export")
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format.",
)
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
@click.option("--key", "keys", multiple=True, help="Specific keys to export (repeatable).")
def cmd_export(fmt, password, keys):
    """Export vault variables to stdout in the chosen format."""
    try:
        selected = list(keys) if keys else None
        output = export_variables(DEFAULT_VAULT, password, fmt=fmt, keys=selected)
        click.echo(output)
    except VaultNotFoundError:
        click.echo("Error: vault not found.", err=True)
        sys.exit(1)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
