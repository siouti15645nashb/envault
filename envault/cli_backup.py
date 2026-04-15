"""CLI commands for vault backup and restore."""

import click
from pathlib import Path

from envault.backup import (
    BackupError,
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
)
from envault.vault import DEFAULT_VAULT_FILE


@click.group(name="backup")
def backup_group():
    """Backup and restore vault files."""


@backup_group.command(name="create")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
def cmd_backup_create(vault):
    """Create a timestamped backup of the vault."""
    try:
        backup_path = create_backup(Path(vault))
        click.echo(f"Backup created: {backup_path}")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@backup_group.command(name="list")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
def cmd_backup_list(vault):
    """List all available backups for the vault."""
    backups = list_backups(Path(vault))
    if not backups:
        click.echo("No backups found.")
        return
    for b in backups:
        click.echo(str(b))


@backup_group.command(name="restore")
@click.argument("backup_file")
@click.option("--vault", default=DEFAULT_VAULT_FILE, show_default=True)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def cmd_backup_restore(backup_file, vault, yes):
    """Restore the vault from a backup file."""
    if not yes:
        click.confirm(
            f"Overwrite '{vault}' with '{backup_file}'?", abort=True
        )
    try:
        restore_backup(Path(backup_file), Path(vault))
        click.echo(f"Vault restored from: {backup_file}")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@backup_group.command(name="delete")
@click.argument("backup_file")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def cmd_backup_delete(backup_file, yes):
    """Delete a specific backup file."""
    if not yes:
        click.confirm(f"Delete backup '{backup_file}'?", abort=True)
    try:
        delete_backup(Path(backup_file))
        click.echo(f"Backup deleted: {backup_file}")
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
