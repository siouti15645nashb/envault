"""CLI commands for promoting variables between vaults."""

import click

from envault.env_promote import PromoteError, promote_variables


@click.group("promote")
def promote_group():
    """Promote variables between vault files."""


@promote_group.command("run")
@click.argument("source", type=click.Path())
@click.argument("dest", type=click.Path())
@click.password_option("--password", "-p", prompt="Vault password", help="Shared vault password.")
@click.option("--key", "-k", multiple=True, help="Specific key(s) to promote. Repeatable.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
def cmd_promote_run(source, dest, password, key, overwrite):
    """Promote variables from SOURCE vault to DEST vault.

    If no --key options are given, all variables are promoted.
    """
    keys = list(key) if key else None
    try:
        result = promote_variables(
            source_vault=source,
            dest_vault=dest,
            password=password,
            keys=keys,
            overwrite=overwrite,
        )
    except PromoteError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if result["promoted"]:
        click.echo(f"Promoted ({len(result['promoted'])}):")        
        for k in result["promoted"]:
            click.echo(f"  + {k}")

    if result["skipped"]:
        click.echo(f"Skipped ({len(result['skipped'])}) — already exist in destination:")
        for k in result["skipped"]:
            click.echo(f"  ~ {k}")

    if result["failed"]:
        click.echo(f"Failed ({len(result['failed'])}):", err=True)
        for entry in result["failed"]:
            click.echo(f"  ! {entry['key']}: {entry['reason']}", err=True)
        raise SystemExit(1)

    if not result["promoted"] and not result["skipped"] and not result["failed"]:
        click.echo("Nothing to promote.")
