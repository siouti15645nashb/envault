"""CLI commands for profile management."""

import click
from envault.profiles import (
    ProfileError,
    save_profile,
    delete_profile,
    list_profiles,
    get_profile,
    apply_profile,
)


@click.group(name="profile")
def profiles_group():
    """Manage named variable profiles."""


@profiles_group.command(name="save")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--dir", "directory", default=".", help="Working directory.")
def cmd_profile_save(name, keys, directory):
    """Save a named profile with the given variable KEYS."""
    try:
        save_profile(name, list(keys), directory)
        click.echo(f"Profile '{name}' saved with {len(keys)} key(s).")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profiles_group.command(name="delete")
@click.argument("name")
@click.option("--dir", "directory", default=".", help="Working directory.")
def cmd_profile_delete(name, directory):
    """Delete a named profile."""
    try:
        delete_profile(name, directory)
        click.echo(f"Profile '{name}' deleted.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profiles_group.command(name="list")
@click.option("--dir", "directory", default=".", help="Working directory.")
def cmd_profile_list(directory):
    """List all saved profiles."""
    names = list_profiles(directory)
    if not names:
        click.echo("No profiles defined.")
    else:
        for n in names:
            click.echo(n)


@profiles_group.command(name="show")
@click.argument("name")
@click.option("--dir", "directory", default=".", help="Working directory.")
def cmd_profile_show(name, directory):
    """Show the keys stored in a profile."""
    try:
        keys = get_profile(name, directory)
        if keys:
            for k in keys:
                click.echo(k)
        else:
            click.echo(f"Profile '{name}' is empty.")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profiles_group.command(name="apply")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--vault", "vault_path", default=".envault", help="Vault file path.")
@click.option("--dir", "directory", default=".", help="Working directory.")
def cmd_profile_apply(name, password, vault_path, directory):
    """Print key=value pairs for all variables in a profile."""
    try:
        values = apply_profile(name, password, vault_path, directory)
        for k, v in values.items():
            if v is None:
                click.echo(f"{k}=(not found)", err=True)
            else:
                click.echo(f"{k}={v}")
    except ProfileError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
