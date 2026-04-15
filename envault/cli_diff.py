"""CLI commands for vault diffing."""

import click

from envault.diff import diff_vault_vs_dotenv, diff_vaults, DiffResult


def _print_diff(result: DiffResult, show_unchanged: bool = False) -> None:
    """Pretty-print a DiffResult to stdout."""
    for key in result.added:
        click.echo(click.style(f"  + {key}", fg="green"))
    for key in result.removed:
        click.echo(click.style(f"  - {key}", fg="red"))
    for key in result.changed:
        click.echo(click.style(f"  ~ {key}", fg="yellow"))
    if show_unchanged:
        for key in result.unchanged:
            click.echo(f"    {key}")
    if not result.has_changes:
        click.echo("No differences found.")
    else:
        click.echo(
            f"\nSummary: {len(result.added)} added, "
            f"{len(result.removed)} removed, "
            f"{len(result.changed)} changed."
        )


@click.group(name="diff")
def diff_group():
    """Compare vault contents with another vault or a .env file."""


@diff_group.command(name="dotenv")
@click.argument("vault_path")
@click.argument("dotenv_path")
@click.password_option("--password", "-p", prompt="Vault password",
                       confirmation_prompt=False, help="Vault password.")
@click.option("--show-unchanged", is_flag=True, default=False,
              help="Also list keys that are identical.")
def cmd_diff_dotenv(vault_path, dotenv_path, password, show_unchanged):
    """Diff VAULT_PATH against a .env file at DOTENV_PATH."""
    try:
        result = diff_vault_vs_dotenv(vault_path, password, dotenv_path)
        _print_diff(result, show_unchanged=show_unchanged)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Diff failed: {exc}")


@diff_group.command(name="vaults")
@click.argument("vault_a")
@click.argument("vault_b")
@click.option("--password-a", prompt="Password for vault A",
              hide_input=True, help="Password for vault A.")
@click.option("--password-b", prompt="Password for vault B",
              hide_input=True, help="Password for vault B.")
@click.option("--show-unchanged", is_flag=True, default=False,
              help="Also list keys that are identical.")
def cmd_diff_vaults(vault_a, vault_b, password_a, password_b, show_unchanged):
    """Diff two vault files against each other."""
    try:
        result = diff_vaults(vault_a, password_a, vault_b, password_b)
        _print_diff(result, show_unchanged=show_unchanged)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Diff failed: {exc}")
