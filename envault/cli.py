"""Main CLI entry point for envault."""

import click
from envault.vault import init_vault, set_variable, get_variable, list_variables
from envault.cli_audit import audit_group
from envault.cli_search import search_group

DEFAULT_VAULT = ".envault"


@click.group()
def cli():
    """envault — encrypted project environment variable manager."""


@cli.command(name="init")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Master password.")
def cmd_init(vault, password):
    """Initialise a new vault."""
    try:
        init_vault(vault, password)
        click.echo(f"Vault initialised at {vault}.")
    except FileExistsError:
        click.echo("Error: vault already exists.", err=True)
        raise SystemExit(1)


@cli.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
def cmd_set(key, value, vault, password):
    """Set a variable in the vault."""
    try:
        set_variable(vault, password, key, value)
        click.echo(f"Set {key}.")
    except FileNotFoundError:
        click.echo("Error: vault not found. Run 'envault init' first.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command(name="get")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
def cmd_get(key, vault, password):
    """Get a variable from the vault."""
    try:
        value = get_variable(vault, password, key)
        click.echo(value)
    except FileNotFoundError:
        click.echo("Error: vault not found.", err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Error: variable '{key}' not found.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cli.command(name="list")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
def cmd_list(vault, password):
    """List all variables in the vault."""
    try:
        variables = list_variables(vault, password)
    except FileNotFoundError:
        click.echo("Error: vault not found.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not variables:
        click.echo("No variables stored.")
        return

    for key in sorted(variables):
        click.echo(key)


cli.add_command(audit_group)
cli.add_command(search_group)


if __name__ == "__main__":
    cli()
