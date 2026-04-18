import click
from envault.vault import VaultError, list_variables
from envault.env_dependency import (
    DependencyError,
    add_dependency,
    remove_dependency,
    get_dependencies,
    list_all_dependencies,
    check_missing,
)

VAULT_FILE = ".envault"


@click.group("dependency")
def dependency_group():
    """Manage variable dependencies."""


@dependency_group.command("add")
@click.argument("key")
@click.argument("depends_on")
def cmd_dependency_add(key, depends_on):
    """Add a dependency: KEY depends on DEPENDS_ON."""
    try:
        add_dependency(VAULT_FILE, key, depends_on)
        click.echo(f"Added: {key} -> {depends_on}")
    except DependencyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@dependency_group.command("remove")
@click.argument("key")
@click.argument("depends_on")
def cmd_dependency_remove(key, depends_on):
    """Remove a dependency from KEY."""
    remove_dependency(VAULT_FILE, key, depends_on)
    click.echo(f"Removed: {key} -> {depends_on}")


@dependency_group.command("list")
@click.argument("key", required=False)
def cmd_dependency_list(key):
    """List dependencies for KEY, or all if omitted."""
    if key:
        deps = get_dependencies(VAULT_FILE, key)
        if deps:
            for d in deps:
                click.echo(f"  {d}")
        else:
            click.echo(f"No dependencies for {key}.")
    else:
        data = list_all_dependencies(VAULT_FILE)
        if not data:
            click.echo("No dependencies defined.")
        else:
            for k, deps in sorted(data.items()):
                click.echo(f"{k}: {', '.join(deps)}")


@dependency_group.command("check")
@click.option("--password", prompt=True, hide_input=True)
def cmd_dependency_check(password):
    """Check for unresolved dependencies against vault keys."""
    try:
        keys = list(list_variables(VAULT_FILE, password).keys())
    except VaultError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    missing = check_missing(VAULT_FILE, keys)
    if not missing:
        click.echo("All dependencies resolved.")
    else:
        for key, absent in sorted(missing.items()):
            click.echo(f"MISSING for {key}: {', '.join(absent)}")
        raise SystemExit(1)
