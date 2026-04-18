"""CLI commands for variable metadata management."""

import click
from envault.env_metadata import (
    MetadataError,
    set_metadata,
    get_metadata,
    remove_metadata_key,
    remove_all_metadata,
    list_metadata,
)

VAULT_FILE = ".envault"


@click.group(name="metadata")
def metadata_group():
    """Manage arbitrary metadata annotations for variables."""


@metadata_group.command(name="set")
@click.argument("key")
@click.argument("meta_key")
@click.argument("meta_value")
def cmd_metadata_set(key, meta_key, meta_value):
    """Set a metadata annotation on a variable."""
    try:
        set_metadata(VAULT_FILE, key, meta_key, meta_value)
        click.echo(f"Metadata '{meta_key}={meta_value}' set on '{key}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@metadata_group.command(name="get")
@click.argument("key")
def cmd_metadata_get(key):
    """Get all metadata annotations for a variable."""
    meta = get_metadata(VAULT_FILE, key)
    if not meta:
        click.echo(f"No metadata for '{key}'.")
    else:
        for mk, mv in meta.items():
            click.echo(f"{mk}={mv}")


@metadata_group.command(name="remove")
@click.argument("key")
@click.argument("meta_key")
def cmd_metadata_remove(key, meta_key):
    """Remove a specific metadata annotation from a variable."""
    try:
        remove_metadata_key(VAULT_FILE, key, meta_key)
        click.echo(f"Metadata '{meta_key}' removed from '{key}'.")
    except MetadataError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@metadata_group.command(name="clear")
@click.argument("key")
def cmd_metadata_clear(key):
    """Remove all metadata annotations from a variable."""
    remove_all_metadata(VAULT_FILE, key)
    click.echo(f"All metadata cleared for '{key}'.")


@metadata_group.command(name="list")
def cmd_metadata_list():
    """List all metadata annotations across all variables."""
    all_meta = list_metadata(VAULT_FILE)
    if not all_meta:
        click.echo("No metadata defined.")
    else:
        for var_key, annotations in all_meta.items():
            for mk, mv in annotations.items():
                click.echo(f"{var_key}  {mk}={mv}")
