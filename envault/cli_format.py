"""CLI commands for managing value format rules."""

import click
from envault.env_format import (
    set_format, remove_format, get_format, list_formats,
    validate_format, SUPPORTED_FORMATS, FormatError
)
from envault.vault import get_variable, VaultError


@click.group(name="format")
def format_group():
    """Manage value format rules for variables."""


@format_group.command("set")
@click.argument("key")
@click.argument("fmt")
@click.option("--vault", default=".envault", show_default=True)
def cmd_format_set(key, fmt, vault):
    """Assign a format rule to a variable."""
    try:
        set_format(vault, key, fmt)
        click.echo(f"Format '{fmt}' assigned to '{key}'.")
    except FormatError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@format_group.command("remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_format_remove(key, vault):
    """Remove format rule from a variable."""
    remove_format(vault, key)
    click.echo(f"Format rule removed from '{key}'.")


@format_group.command("get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_format_get(key, vault):
    """Show the format rule for a variable."""
    fmt = get_format(vault, key)
    if fmt:
        click.echo(fmt)
    else:
        click.echo(f"No format rule set for '{key}'.")


@format_group.command("list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_format_list(vault):
    """List all format rules."""
    data = list_formats(vault)
    if not data:
        click.echo("No format rules defined.")
    else:
        for k, v in data.items():
            click.echo(f"{k}: {v}")


@format_group.command("check")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_format_check(key, vault, password):
    """Check if a variable's value matches its format rule."""
    fmt = get_format(vault, key)
    if not fmt:
        click.echo(f"No format rule set for '{key}'.")
        return
    try:
        value = get_variable(vault, password, key)
        if validate_format(value, fmt):
            click.echo(f"'{key}' matches format '{fmt}'.")
        else:
            click.echo(f"'{key}' does NOT match format '{fmt}'.", err=True)
            raise SystemExit(1)
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
