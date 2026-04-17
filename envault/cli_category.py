"""CLI commands for variable category management."""
import click
from envault.env_category import (
    set_category, remove_category, get_category,
    list_categories, find_by_category, CategoryError
)


@click.group(name="category")
def category_group():
    """Manage variable categories."""


@category_group.command(name="set")
@click.argument("key")
@click.argument("category")
@click.option("--vault", default=".envault", show_default=True)
def cmd_category_set(key, category, vault):
    """Assign a category to a variable."""
    try:
        set_category(vault, key, category)
        click.echo(f"Category '{category}' set for '{key}'.")
    except CategoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@category_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_category_remove(key, vault):
    """Remove the category from a variable."""
    try:
        remove_category(vault, key)
        click.echo(f"Category removed from '{key}'.")
    except CategoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@category_group.command(name="get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_category_get(key, vault):
    """Get the category of a variable."""
    cat = get_category(vault, key)
    if cat:
        click.echo(cat)
    else:
        click.echo(f"No category set for '{key}'.")


@category_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_category_list(vault):
    """List all variable categories."""
    data = list_categories(vault)
    if not data:
        click.echo("No categories defined.")
    else:
        for k, v in sorted(data.items()):
            click.echo(f"{k}: {v}")


@category_group.command(name="find")
@click.argument("category")
@click.option("--vault", default=".envault", show_default=True)
def cmd_category_find(category, vault):
    """Find variables by category."""
    keys = find_by_category(vault, category)
    if not keys:
        click.echo(f"No variables in category '{category}'.")
    else:
        for k in sorted(keys):
            click.echo(k)
