"""CLI commands for per-variable cipher management."""

import click
from envault.env_cipher import (
    set_cipher, get_cipher, remove_cipher, list_ciphers,
    VALID_CIPHERS, CipherError
)


@click.group("cipher")
def cipher_group():
    """Manage per-variable cipher algorithm settings."""


@cipher_group.command("set")
@click.argument("key")
@click.argument("cipher")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_cipher_set(key, cipher, vault_dir):
    """Set cipher algorithm for a variable."""
    try:
        set_cipher(vault_dir, key, cipher)
        click.echo(f"Cipher for '{key}' set to '{cipher}'.")
    except CipherError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cipher_group.command("get")
@click.argument("key")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_cipher_get(key, vault_dir):
    """Get cipher algorithm for a variable."""
    cipher = get_cipher(vault_dir, key)
    if cipher:
        click.echo(cipher)
    else:
        click.echo(f"No cipher set for '{key}' (default used).")


@cipher_group.command("remove")
@click.argument("key")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_cipher_remove(key, vault_dir):
    """Remove cipher setting for a variable."""
    try:
        remove_cipher(vault_dir, key)
        click.echo(f"Cipher setting removed for '{key}'.")
    except CipherError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@cipher_group.command("list")
@click.option("--dir", "vault_dir", default=".", show_default=True)
def cmd_cipher_list(vault_dir):
    """List all cipher settings."""
    data = list_ciphers(vault_dir)
    if not data:
        click.echo("No cipher settings defined.")
        return
    for key, cipher in sorted(data.items()):
        click.echo(f"{key}: {cipher}")


@cipher_group.command("valid")
def cmd_cipher_valid():
    """List valid cipher algorithms."""
    for c in VALID_CIPHERS:
        click.echo(c)
