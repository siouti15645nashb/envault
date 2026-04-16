"""CLI commands for variable expiry management."""

import os
from datetime import datetime, timezone

import click

from .env_expiry import (
    ExpiryError, set_expiry, remove_expiry, get_expiry,
    list_expiring, get_expired,
)

VAULT_FILE = ".envault.json"


@click.group(name="expiry")
def expiry_group():
    """Manage variable expiry/TTL."""


@expiry_group.command("set")
@click.argument("key")
@click.argument("expires_at")  # ISO format: 2025-12-31T00:00:00
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_expiry_set(key, expires_at, vault):
    """Set expiry for KEY (ISO datetime, UTC)."""
    vault_dir = os.path.dirname(os.path.abspath(vault))
    try:
        dt = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
        set_expiry(vault_dir, key, dt)
        click.echo(f"Expiry set for '{key}': {dt.isoformat()}")
    except ValueError as e:
        click.echo(f"Invalid datetime format: {e}", err=True)
        raise SystemExit(1)


@expiry_group.command("remove")
@click.argument("key")
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_expiry_remove(key, vault):
    """Remove expiry for KEY."""
    vault_dir = os.path.dirname(os.path.abspath(vault))
    try:
        remove_expiry(vault_dir, key)
        click.echo(f"Expiry removed for '{key}'.")
    except ExpiryError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@expiry_group.command("list")
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_expiry_list(vault):
    """List all variables with expiry set."""
    vault_dir = os.path.dirname(os.path.abspath(vault))
    entries = list_expiring(vault_dir)
    if not entries:
        click.echo("No expiry entries found.")
        return
    for key, dt in sorted(entries.items()):
        click.echo(f"{key}: {dt.isoformat()}")


@expiry_group.command("check")
@click.option("--vault", default=VAULT_FILE, show_default=True)
def cmd_expiry_check(vault):
    """List variables that have expired."""
    vault_dir = os.path.dirname(os.path.abspath(vault))
    expired = get_expired(vault_dir)
    if not expired:
        click.echo("No expired variables.")
        return
    click.echo("Expired variables:")
    for key in expired:
        click.echo(f"  {key}")
    raise SystemExit(1)
