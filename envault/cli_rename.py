"""CLI commands for renaming and copying vault variables."""

import click
from envault.rename import RenameError, rename_variable, rename_variable_force, copy_variable
from envault.vault import VaultError

DEFAULT_VAULT = ".envault"


@click.group(name="rename")
def rename_group():
    """Rename or copy variables within the vault."""


@rename_group.command(name="mv")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--force", is_flag=True, default=False, help="Overwrite new_key if it exists.")
def cmd_rename_mv(old_key, new_key, vault, password, force):
    """Rename OLD_KEY to NEW_KEY in the vault."""
    try:
        if force:
            rename_variable_force(vault, password, old_key, new_key)
        else:
            rename_variable(vault, password, old_key, new_key)
        click.echo(f"Renamed '{old_key}' to '{new_key}'.")
    except RenameError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except VaultError as e:
        click.echo(f"Vault error: {e}", err=True)
        raise SystemExit(1)


@rename_group.command(name="cp")
@click.argument("src_key")
@click.argument("dst_key")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def cmd_rename_cp(src_key, dst_key, vault, password):
    """Copy SRC_KEY to DST_KEY in the vault."""
    try:
        copy_variable(vault, password, src_key, dst_key)
        click.echo(f"Copied '{src_key}' to '{dst_key}'.")
    except RenameError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except VaultError as e:
        click.echo(f"Vault error: {e}", err=True)
        raise SystemExit(1)
