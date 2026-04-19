import click
from envault.env_masking import (
    enable_masking,
    disable_masking,
    is_masked,
    list_masked,
    MaskingError,
)


@click.group(name="mask")
def masking_group():
    """Manage value masking for sensitive variables."""


@masking_group.command(name="enable")
@click.argument("key")
@click.option("--visible", default=4, show_default=True, help="Number of visible characters.")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_mask_enable(key, visible, vault_dir):
    """Enable masking for a variable."""
    try:
        enable_masking(vault_dir, key, visible_chars=visible)
        click.echo(f"Masking enabled for '{key}' (visible chars: {visible}).")
    except MaskingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@masking_group.command(name="disable")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_mask_disable(key, vault_dir):
    """Disable masking for a variable."""
    try:
        disable_masking(vault_dir, key)
        click.echo(f"Masking disabled for '{key}'.")
    except MaskingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@masking_group.command(name="check")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_mask_check(key, vault_dir):
    """Check if a variable is masked."""
    masked = is_masked(vault_dir, key)
    status = "masked" if masked else "not masked"
    click.echo(f"'{key}' is {status}.")


@masking_group.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_mask_list(vault_dir):
    """List all masked variables."""
    keys = list_masked(vault_dir)
    if not keys:
        click.echo("No masked variables.")
    else:
        for k in keys:
            click.echo(k)
