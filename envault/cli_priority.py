"""CLI commands for managing variable priority levels."""

import click
from envault.env_priority import (
    set_priority, get_priority, remove_priority,
    list_priorities, get_by_level, PriorityError, VALID_LEVELS
)


@click.group(name="priority")
def priority_group():
    """Manage priority levels for environment variables."""


@priority_group.command(name="set")
@click.argument("key")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--vault", default=".envault", show_default=True)
def cmd_priority_set(key, level, vault):
    """Set priority level for a variable."""
    try:
        set_priority(vault, key, level)
        click.echo(f"Priority for '{key}' set to '{level}'.")
    except PriorityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@priority_group.command(name="get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_priority_get(key, vault):
    """Get priority level of a variable."""
    level = get_priority(vault, key)
    click.echo(f"{key}: {level}")


@priority_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_priority_remove(key, vault):
    """Remove priority override for a variable (resets to 'normal')."""
    remove_priority(vault, key)
    click.echo(f"Priority for '{key}' removed.")


@priority_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_priority_list(vault):
    """List all variables with explicit priority levels."""
    data = list_priorities(vault)
    if not data:
        click.echo("No priority levels set.")
        return
    for key, level in sorted(data.items()):
        click.echo(f"{key}: {level}")


@priority_group.command(name="find")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--vault", default=".envault", show_default=True)
def cmd_priority_find(level, vault):
    """Find all variables with a given priority level."""
    try:
        keys = get_by_level(vault, level)
    except PriorityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if not keys:
        click.echo(f"No variables with priority '{level}'.")
        return
    for key in sorted(keys):
        click.echo(key)
