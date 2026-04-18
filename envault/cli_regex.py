"""CLI commands for regex pattern constraints."""
import click
from envault.env_regex import (
    RegexError,
    set_pattern,
    remove_pattern,
    get_pattern,
    list_patterns,
    validate_against_pattern,
)


@click.group(name="regex")
def regex_group():
    """Manage regex pattern constraints for variables."""


@regex_group.command(name="set")
@click.argument("key")
@click.argument("pattern")
@click.option("--vault", default=".envault", show_default=True)
def cmd_regex_set(key, pattern, vault):
    """Set a regex pattern constraint for KEY."""
    try:
        set_pattern(vault, key, pattern)
        click.echo(f"Pattern set for '{key}': {pattern}")
    except RegexError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@regex_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_regex_remove(key, vault):
    """Remove the regex pattern constraint for KEY."""
    try:
        remove_pattern(vault, key)
        click.echo(f"Pattern removed for '{key}'.")
    except RegexError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@regex_group.command(name="get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_regex_get(key, vault):
    """Show the regex pattern for KEY."""
    pattern = get_pattern(vault, key)
    if pattern is None:
        click.echo(f"No pattern defined for '{key}'.")
    else:
        click.echo(pattern)


@regex_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_regex_list(vault):
    """List all regex pattern constraints."""
    patterns = list_patterns(vault)
    if not patterns:
        click.echo("No patterns defined.")
    else:
        for k, v in patterns.items():
            click.echo(f"{k}: {v}")


@regex_group.command(name="check")
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=".envault", show_default=True)
def cmd_regex_check(key, value, vault):
    """Check VALUE against the regex pattern for KEY."""
    if validate_against_pattern(vault, key, value):
        click.echo("OK")
    else:
        click.echo(f"Value does not match pattern for '{key}'.", err=True)
        raise SystemExit(1)
