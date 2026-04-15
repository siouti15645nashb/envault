"""CLI commands for env-check — compare vault vs live environment."""

from __future__ import annotations

import sys
import click

from envault.env_check import check_env
from envault.vault import VaultError

VAULT_FILE = ".envault"


@click.group("env-check")
def env_check_group():
    """Compare vault variables against the current environment."""


@env_check_group.command("run")
@click.option("--vault", default=VAULT_FILE, show_default=True, help="Path to vault file.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--show-extra", is_flag=True, default=False, help="Report env vars not in vault.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on any issue.")
def cmd_env_check_run(vault: str, password: str, show_extra: bool, strict: bool):
    """Check that all vault variables are present and correct in the current environment."""
    try:
        result = check_env(vault, password, include_extra=show_extra)
    except VaultError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if result.matched:
        click.echo(click.style(f"  OK  ({len(result.matched)} matched)", fg="green"))

    for key in result.missing:
        click.echo(click.style(f"  MISSING     {key}", fg="red"))

    for key in result.mismatched:
        click.echo(click.style(f"  MISMATCH    {key}", fg="yellow"))

    if show_extra:
        for key in result.extra:
            click.echo(click.style(f"  EXTRA       {key}", fg="cyan"))

    if result.has_issues:
        click.echo(click.style("\nIssues found.", fg="red"))
        if strict:
            sys.exit(1)
    else:
        click.echo(click.style("\nAll vault variables match the environment.", fg="green"))
