"""CLI commands for linting vault variable names and values."""

import click

from envault.lint import lint_vault, LintIssue
from envault.vault import VaultError


@click.group(name="lint")
def lint_group():
    """Lint environment variable names and values."""


@lint_group.command(name="check")
@click.argument("vault_path", default=".envault")
@click.password_option("--password", "-p", prompt="Vault password",
                       confirmation_prompt=False, help="Vault password.")
@click.option("--strict", is_flag=True, default=False,
              help="Exit with non-zero code if any warnings are found.")
def cmd_lint_check(vault_path: str, password: str, strict: bool):
    """Check vault variables for naming and value issues."""
    try:
        issues = lint_vault(vault_path, password)
    except VaultError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not issues:
        click.echo(click.style("✔ No lint issues found.", fg="green"))
        return

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    for issue in issues:
        colour = "red" if issue.severity == "error" else "yellow"
        label = issue.severity.upper()
        click.echo(click.style(f"[{label}] {issue.key}: {issue.message}", fg=colour))

    click.echo(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")

    if errors or (strict and warnings):
        raise SystemExit(1)


@lint_group.command(name="rules")
def cmd_lint_rules():
    """List all available lint rules."""
    from envault.lint import LINT_RULES
    click.echo("Available lint rules:")
    for rule in LINT_RULES:
        click.echo(f"  - {rule}")
