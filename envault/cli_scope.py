import click
from envault.env_scope import (
    set_scope, get_scope, remove_scope, list_scopes,
    filter_by_scope, VALID_SCOPES, ScopeError
)


@click.group(name="scope")
def scope_group():
    """Manage variable scopes (local, development, staging, production, global)."""
    pass


@scope_group.command(name="set")
@click.argument("key")
@click.argument("scope")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_scope_set(key, scope, vault_dir):
    """Assign a scope to a variable."""
    try:
        set_scope(vault_dir, key, scope)
        click.echo(f"Scope '{scope}' assigned to '{key}'.")
    except ScopeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@scope_group.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_scope_get(key, vault_dir):
    """Get the scope of a variable."""
    scope = get_scope(vault_dir, key)
    click.echo(scope)


@scope_group.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_scope_remove(key, vault_dir):
    """Remove scope assignment from a variable."""
    removed = remove_scope(vault_dir, key)
    if removed:
        click.echo(f"Scope removed from '{key}'.")
    else:
        click.echo(f"No scope set for '{key}'.")


@scope_group.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_scope_list(vault_dir):
    """List all scope assignments."""
    data = list_scopes(vault_dir)
    if not data:
        click.echo("No scopes defined.")
        return
    for key, scope in sorted(data.items()):
        click.echo(f"{key}: {scope}")


@scope_group.command(name="filter")
@click.argument("scope")
@click.option("--vault-dir", default=".", show_default=True)
def cmd_scope_filter(scope, vault_dir):
    """List all variables with a given scope."""
    try:
        keys = filter_by_scope(vault_dir, scope)
    except ScopeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if not keys:
        click.echo(f"No variables with scope '{scope}'.")
        return
    for k in sorted(keys):
        click.echo(k)
