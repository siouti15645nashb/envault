"""cli_status.py — CLI commands for vault status reporting."""

import click
from envault.env_status import get_status


@click.group(name="status")
def status_group():
    """Vault status and health reporting."""


@status_group.command(name="show")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def cmd_status_show(vault_path: str, password: str):
    """Show an aggregate status report for the vault."""
    try:
        report = get_status(vault_path, password)
    except Exception as e:
        raise click.ClickException(str(e))

    click.echo(f"Vault : {report.vault_path}")
    click.echo(f"Total keys      : {report.total_keys}")
    click.echo(f"Locked          : {len(report.locked_keys)}")
    click.echo(f"Pinned          : {len(report.pinned_keys)}")
    click.echo(f"Sensitive       : {len(report.sensitive_keys)}")
    click.echo(f"Read-only       : {len(report.readonly_keys)}")
    click.echo(f"Required        : {len(report.required_keys)}")

    if report.expiring_keys:
        click.secho(f"Expired/Expiring: {', '.join(report.expiring_keys)}", fg="red")
    else:
        click.echo("Expired/Expiring: none")


@status_group.command(name="issues")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt=True, help="Vault password.")
def cmd_status_issues(vault_path: str, password: str):
    """Exit non-zero if the vault has any status issues."""
    try:
        report = get_status(vault_path, password)
    except Exception as e:
        raise click.ClickException(str(e))

    if report.has_issues():
        click.secho("Issues found:", fg="red")
        for k in report.expiring_keys:
            click.echo(f"  [EXPIRED] {k}")
        raise SystemExit(1)
    else:
        click.secho("No issues found.", fg="green")
