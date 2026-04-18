"""CLI commands for access control."""

import click
from envault.env_access import set_access, get_access, remove_access, list_access, AccessError


@click.group(name="access")
def access_group():
    """Manage read/write access control for variables."""


@access_group.command(name="set")
@click.argument("key")
@click.option("--reader", multiple=True, help="Users allowed to read.")
@click.option("--writer", multiple=True, help="Users allowed to write.")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_access_set(key, reader, writer, vault_dir):
    """Set access control for KEY."""
    try:
        set_access(vault_dir, key, list(reader), list(writer))
        click.echo(f"Access set for '{key}'.")
    except AccessError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@access_group.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_access_get(key, vault_dir):
    """Show access control for KEY."""
    entry = get_access(vault_dir, key)
    readers = ", ".join(entry["readers"]) or "(all)"
    writers = ", ".join(entry["writers"]) or "(all)"
    click.echo(f"readers: {readers}")
    click.echo(f"writers: {writers}")


@access_group.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_access_remove(key, vault_dir):
    """Remove access control for KEY."""
    removed = remove_access(vault_dir, key)
    if removed:
        click.echo(f"Access entry for '{key}' removed.")
    else:
        click.echo(f"No access entry found for '{key}'.")


@access_group.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_access_list(vault_dir):
    """List all access control entries."""
    data = list_access(vault_dir)
    if not data:
        click.echo("No access entries defined.")
        return
    for key, entry in sorted(data.items()):
        readers = ", ".join(entry.get("readers", [])) or "(all)"
        writers = ", ".join(entry.get("writers", [])) or "(all)"
        click.echo(f"{key}: readers=[{readers}] writers=[{writers}]")
