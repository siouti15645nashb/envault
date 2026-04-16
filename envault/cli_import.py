"""CLI commands for importing environment variables from .env files."""

import click

from envault.import_env import import_from_dotenv, ImportError as EnvImportError
from envault.vault import VaultError

DEFAULT_VAULT = ".envault"


@click.group(name="import")
def import_group():
    """Import variables from external sources."""


@import_group.command(name="dotenv")
@click.argument("dotenv_path")
@click.option("--vault", default=DEFAULT_VAULT, show_default=True, help="Path to the vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing keys.",
)
def cmd_import_dotenv(dotenv_path, vault, password, overwrite):
    """Import variables from a .env file into the vault."""
    try:
        imported, skipped = import_from_dotenv(
            vault_path=vault,
            dotenv_path=dotenv_path,
            password=password,
            overwrite=overwrite,
        )
    except EnvImportError as e:
        click.echo(f"Import error: {e}", err=True)
        raise SystemExit(1)
    except VaultError as e:
        click.echo(f"Vault error: {e}", err=True)
        raise SystemExit(1)

    if imported:
        click.echo(f"Imported {len(imported)} variable(s): {', '.join(imported)}")
    else:
        click.echo("No variables imported.")

    if skipped:
        click.echo(
            f"Skipped {len(skipped)} existing variable(s): {', '.join(skipped)}"
            " (use --overwrite to replace them)"
        )
