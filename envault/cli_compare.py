"""CLI commands for comparing vaults."""
import click
from envault.env_compare import compare_vaults, CompareError


@click.group(name="compare")
def compare_group():
    """Compare variables across vault files."""


@compare_group.command(name="run")
@click.argument("vault_a", type=click.Path())
@click.argument("vault_b", type=click.Path())
@click.option("--password-a", prompt="Password for vault A", hide_input=True)
@click.option("--password-b", prompt="Password for vault B", hide_input=True)
@click.option("--only-diff", is_flag=True, default=False, help="Show only differences.")
def cmd_compare_run(vault_a, vault_b, password_a, password_b, only_diff):
    """Compare two vault files and display differences."""
    try:
        result = compare_vaults(vault_a, password_a, vault_b, password_b)
    except CompareError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    if result.only_in_a:
        click.echo("Only in A:")
        for k in result.only_in_a:
            click.echo(f"  - {k}")

    if result.only_in_b:
        click.echo("Only in B:")
        for k in result.only_in_b:
            click.echo(f"  + {k}")

    if result.different:
        click.echo("Different values:")
        for k in result.different:
            click.echo(f"  ~ {k}")

    if not only_diff and result.same:
        click.echo("Same:")
        for k in result.same:
            click.echo(f"    {k}")

    if not result.has_differences():
        click.echo("Vaults are identical.")
    else:
        raise SystemExit(1)
