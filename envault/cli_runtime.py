"""CLI commands for runtime environment bindings."""

import click
from envault.env_runtime import (
    set_runtime, get_runtime, remove_runtime, list_runtime,
    filter_by_target, VALID_TARGETS, RuntimeError
)


@click.group(name="runtime")
def runtime_group():
    """Manage runtime target bindings for vault keys."""


@runtime_group.command(name="set")
@click.argument("key")
@click.argument("target")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_runtime_set(key, target, vault_dir):
    """Bind KEY to a runtime TARGET."""
    try:
        set_runtime(vault_dir, key, target)
        click.echo(f"Bound '{key}' to runtime '{target}'.")
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@runtime_group.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_runtime_get(key, vault_dir):
    """Get the runtime target for KEY."""
    val = get_runtime(vault_dir, key)
    if val is None:
        click.echo(f"No runtime binding for '{key}'.")
    else:
        click.echo(val)


@runtime_group.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_runtime_remove(key, vault_dir):
    """Remove runtime binding for KEY."""
    try:
        remove_runtime(vault_dir, key)
        click.echo(f"Removed runtime binding for '{key}'.")
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@runtime_group.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--target", default=None, help="Filter by target.")
def cmd_runtime_list(vault_dir, target):
    """List all runtime bindings."""
    if target:
        keys = filter_by_target(vault_dir, target)
        for k in keys:
            click.echo(f"{k}: {target}")
        if not keys:
            click.echo(f"No keys bound to '{target}'.")
    else:
        data = list_runtime(vault_dir)
        if not data:
            click.echo("No runtime bindings defined.")
        else:
            for k, v in data.items():
                click.echo(f"{k}: {v}")


@runtime_group.command(name="targets")
def cmd_runtime_targets():
    """List valid runtime targets."""
    for t in VALID_TARGETS:
        click.echo(t)
