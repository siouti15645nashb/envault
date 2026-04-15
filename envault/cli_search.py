"""CLI commands for searching vault variables."""

import click
from envault.search import search_variables, filter_by_prefix

DEFAULT_VAULT = ".envault"


@click.group(name="search")
def search_group():
    """Search and filter vault variables."""


@search_group.command(name="find")
@click.argument("pattern")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive search.")
def cmd_search_find(pattern, vault, password, case_sensitive):
    """Find variables whose names contain PATTERN."""
    try:
        results = search_variables(vault, password, pattern, case_sensitive=case_sensitive)
    except FileNotFoundError:
        click.echo("Error: vault not found. Run 'envault init' first.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not results:
        click.echo(f"No variables matching '{pattern}'.")
        return

    for key, value in sorted(results.items()):
        click.echo(f"{key}={value}")


@search_group.command(name="prefix")
@click.argument("prefix")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Master password.")
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive match.")
def cmd_search_prefix(prefix, vault, password, case_sensitive):
    """List variables whose names start with PREFIX."""
    try:
        results = filter_by_prefix(vault, password, prefix, case_sensitive=case_sensitive)
    except FileNotFoundError:
        click.echo("Error: vault not found. Run 'envault init' first.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if not results:
        click.echo(f"No variables with prefix '{prefix}'.")
        return

    for key, value in sorted(results.items()):
        click.echo(f"{key}={value}")
