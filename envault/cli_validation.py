"""CLI commands for env variable validation rules."""

import click
from envault.vault import VaultError, get_variable, list_variables
from envault.env_validation import (
    VALIDATION_RULES, ValidationError, validate_all, validate_value
)


@click.group(name="validate")
def validation_group():
    """Manage and run validation rules on variables."""


@validation_group.command(name="run")
@click.argument("vault_path")
@click.argument("password")
@click.option("--rule", multiple=True, help="Rule to apply to all variables")
def cmd_validate_run(vault_path, password, rule):
    """Run validation rules against all variables in the vault."""
    if not rule:
        click.echo("No rules specified. Use --rule to specify rules.")
        raise SystemExit(1)
    try:
        keys = list_variables(vault_path, password)
        variables = {k: get_variable(vault_path, password, k) for k in keys}
    except VaultError as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

    rule_map = {k: list(rule) for k in variables}
    try:
        results = validate_all(variables, rule_map)
    except ValidationError as e:
        click.echo(f"Validation error: {e}")
        raise SystemExit(1)

    failed = False
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        msg = f" ({r.message})" if r.message else ""
        click.echo(f"[{status}] {r.key} [{r.rule}]{msg}")
        if not r.passed:
            failed = True

    if failed:
        raise SystemExit(1)


@validation_group.command(name="rules")
def cmd_validate_rules():
    """List all available validation rules."""
    for name, fn in VALIDATION_RULES.items():
        _, desc = fn("__probe__") if False else (None, None)
        click.echo(f"  {name}")
