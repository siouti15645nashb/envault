"""CLI commands for TTL management."""

import click
from envault.env_ttl import TTLError, set_ttl, remove_ttl, list_ttl, get_expired_keys, is_expired


@click.group(name="ttl")
def ttl_group():
    """Manage time-to-live for variables."""


@ttl_group.command(name="set")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault", default=".envault", show_default=True)
def cmd_ttl_set(key, seconds, vault):
    """Set a TTL (in seconds) for KEY."""
    try:
        expiry = set_ttl(vault, key, seconds)
        click.echo(f"TTL set for '{key}': expires at {expiry.isoformat()} UTC")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_ttl_remove(key, vault):
    """Remove TTL for KEY."""
    try:
        remove_ttl(vault, key)
        click.echo(f"TTL removed for '{key}'.")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_ttl_list(vault):
    """List all TTL entries."""
    data = list_ttl(vault)
    if not data:
        click.echo("No TTL entries set.")
        return
    for key, expiry in sorted(data.items()):
        click.echo(f"{key}: {expiry} UTC")


@ttl_group.command(name="check")
@click.option("--vault", default=".envault", show_default=True)
def cmd_ttl_check(vault):
    """List expired keys."""
    expired = get_expired_keys(vault)
    if not expired:
        click.echo("No expired keys.")
        return
    click.echo("Expired keys:")
    for key in expired:
        click.echo(f"  {key}")
    raise SystemExit(1)
