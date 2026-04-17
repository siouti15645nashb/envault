"""CLI commands for managing variable descriptions."""

import click
from envault.env_description import (
    DescriptionError,
    set_description,
    get_description,
    remove_description,
    list_descriptions,
)

DEFAULT_VAULT = ".envault"


@click.group(name="desc")
def desc_group():
    """Manage descriptions for vault variables."""


@desc_group.command(name="set")
@click.argument("key")
@click.argument("description")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_desc_set(key, description, vault):
    """Set a description for a variable."""
    try:
        set_description(vault, key, description)
        click.echo(f"Description set for '{key}'.")
    except DescriptionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@desc_group.command(name="get")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_desc_get(key, vault):
    """Get the description for a variable."""
    desc = get_description(vault, key)
    if desc is None:
        click.echo(f"No description set for '{key}'.")
    else:
        click.echo(desc)


@desc_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_desc_remove(key, vault):
    """Remove the description for a variable."""
    try:
        remove_description(vault, key)
        click.echo(f"Description removed for '{key}'.")
    except DescriptionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@desc_group.command(name="list")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True)
def cmd_desc_list(vault):
    """List all variable descriptions."""
    data = list_descriptions(vault)
    if not data:
        click.echo("No descriptions set.")
    else:
        for key, desc in sorted(data.items()):
            click.echo(f"{key}: {desc}")
