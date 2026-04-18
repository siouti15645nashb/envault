import click
from envault.env_severity import (
    set_severity, get_severity, remove_severity,
    list_severity, get_by_level, SeverityError, VALID_LEVELS
)


@click.group(name="severity")
def severity_group():
    """Manage severity levels for environment variables."""
    pass


@severity_group.command(name="set")
@click.argument("key")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_severity_set(key, level, vault_dir):
    """Set severity level for a variable."""
    try:
        set_severity(vault_dir, key, level)
        click.echo(f"Severity for '{key}' set to '{level}'.")
    except SeverityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@severity_group.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_severity_get(key, vault_dir):
    """Get severity level for a variable."""
    level = get_severity(vault_dir, key)
    if level is None:
        click.echo(f"No severity set for '{key}'.")
    else:
        click.echo(f"{key}: {level}")


@severity_group.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_severity_remove(key, vault_dir):
    """Remove severity level for a variable."""
    try:
        remove_severity(vault_dir, key)
        click.echo(f"Severity removed for '{key}'.")
    except SeverityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@severity_group.command(name="list")
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_severity_list(vault_dir):
    """List all severity levels."""
    data = list_severity(vault_dir)
    if not data:
        click.echo("No severity levels set.")
    else:
        for key, level in sorted(data.items()):
            click.echo(f"{key}: {level}")


@severity_group.command(name="find")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--vault-dir", default=".", help="Vault directory")
def cmd_severity_find(level, vault_dir):
    """Find all variables with a given severity level."""
    try:
        keys = get_by_level(vault_dir, level)
        if not keys:
            click.echo(f"No variables with severity '{level}'.")
        else:
            for k in sorted(keys):
                click.echo(k)
    except SeverityError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
