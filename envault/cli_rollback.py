import click
from envault.env_rollback import (
    create_snapshot, list_snapshots, rollback_to, delete_snapshot, RollbackError
)
import time


@click.group(name="rollback")
def rollback_group():
    """Manage vault snapshots and rollback."""
    pass


@rollback_group.command(name="snapshot")
@click.argument("vault_path")
@click.option("--label", default="", help="Optional label for the snapshot.")
def cmd_rollback_snapshot(vault_path, label):
    """Create a snapshot of the current vault state."""
    try:
        snap = create_snapshot(vault_path, label=label)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(snap["timestamp"]))
        click.echo(f"Snapshot created at {ts} with {len(snap['variables'])} variable(s).")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rollback_group.command(name="list")
@click.argument("vault_path")
def cmd_rollback_list(vault_path):
    """List all available snapshots."""
    snapshots = list_snapshots(vault_path)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for i, snap in enumerate(snapshots):
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(snap["timestamp"]))
        label = f" [{snap['label']}]" if snap.get("label") else ""
        count = len(snap.get("variables", {}))
        click.echo(f"[{i}] {ts}{label} — {count} variable(s)")


@rollback_group.command(name="restore")
@click.argument("vault_path")
@click.argument("index", type=int)
@click.option("--password", prompt=True, hide_input=True)
def cmd_rollback_restore(vault_path, index, password):
    """Restore vault to a previous snapshot by index."""
    try:
        count = rollback_to(vault_path, index, password)
        click.echo(f"Restored {count} variable(s) from snapshot [{index}].")
    except RollbackError as e:
        click.echo(f"Rollback error: {e}", err=True)
        raise SystemExit(1)


@rollback_group.command(name="delete")
@click.argument("vault_path")
@click.argument("index", type=int)
def cmd_rollback_delete(vault_path, index):
    """Delete a snapshot by index."""
    try:
        delete_snapshot(vault_path, index)
        click.echo(f"Snapshot [{index}] deleted.")
    except RollbackError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
