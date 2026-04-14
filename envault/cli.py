"""CLI entry point for envault using Click."""

import sys
import click
from envault.vault import init_vault, set_variable, get_variable, list_variables, delete_variable


@click.group()
def cli():
    """envault — manage and encrypt project-level environment variables."""
    pass


@cli.command("init")
def cmd_init():
    """Initialize a new vault in the current directory."""
    try:
        init_vault()
        click.echo("Vault initialized successfully. A .envault file has been created.")
    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.password_option("--password", "-p", prompt="Vault password", help="Encryption password.")
def cmd_set(key, value, password):
    """Set an encrypted environment variable."""
    try:
        set_variable(key, value, password)
        click.echo(f"Variable '{key}' set successfully.")
    except FileNotFoundError:
        click.echo("Error: No vault found. Run 'envault init' first.", err=True)
        sys.exit(1)


@cli.command("get")
@click.argument("key")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False, help="Encryption password.")
def cmd_get(key, password):
    """Retrieve and decrypt an environment variable."""
    try:
        value = get_variable(key, password)
        if value is None:
            click.echo(f"Error: Variable '{key}' not found.", err=True)
            sys.exit(1)
        click.echo(value)
    except FileNotFoundError:
        click.echo("Error: No vault found. Run 'envault init' first.", err=True)
        sys.exit(1)
    except Exception:
        click.echo("Error: Decryption failed. Wrong password?", err=True)
        sys.exit(1)


@cli.command("list")
def cmd_list():
    """List all stored variable keys."""
    try:
        keys = list_variables()
        if not keys:
            click.echo("No variables stored in vault.")
        else:
            for key in keys:
                click.echo(key)
    except FileNotFoundError:
        click.echo("Error: No vault found. Run 'envault init' first.", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("key")
def cmd_delete(key):
    """Delete an environment variable from the vault."""
    try:
        removed = delete_variable(key)
        if removed:
            click.echo(f"Variable '{key}' deleted.")
        else:
            click.echo(f"Error: Variable '{key}' not found.", err=True)
            sys.exit(1)
    except FileNotFoundError:
        click.echo("Error: No vault found. Run 'envault init' first.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
