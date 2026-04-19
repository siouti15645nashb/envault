import click
from envault.env_quota import (
    QuotaError,
    set_quota,
    get_quota,
    remove_quota,
    check_quota,
    DEFAULT_MAX_KEYS,
)
from envault.vault import list_variables


@click.group(name="quota")
def quota_group():
    """Manage vault key quota limits."""


@quota_group.command(name="set")
@click.argument("max_keys", type=int)
@click.option("--vault-dir", default=".", show_default=True)
def cmd_quota_set(max_keys, vault_dir):
    """Set the maximum number of keys allowed in the vault."""
    try:
        set_quota(vault_dir, max_keys)
        click.echo(f"Quota set: max {max_keys} keys.")
    except QuotaError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@quota_group.command(name="get")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_quota_get(vault_dir):
    """Show the current quota limit."""
    limit = get_quota(vault_dir)
    default_note = " (default)" if limit == DEFAULT_MAX_KEYS else ""
    click.echo(f"Max keys: {limit}{default_note}")


@quota_group.command(name="remove")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_quota_remove(vault_dir):
    """Remove the quota limit (resets to default)."""
    remove_quota(vault_dir)
    click.echo("Quota removed. Default limit applies.")


@quota_group.command(name="check")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_quota_check(vault_dir, password):
    """Check whether the vault is within its quota."""
    try:
        keys = list_variables(vault_dir, password)
        count = len(keys)
        within = check_quota(vault_dir, count)
        limit = get_quota(vault_dir)
        status = "OK" if within else "EXCEEDED"
        click.echo(f"Keys: {count} / {limit} [{status}]")
        if not within:
            raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
