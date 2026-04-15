"""CLI commands for template management."""

import click
from envault.templates import (
    TemplateError,
    save_template,
    delete_template,
    get_template,
    list_templates,
    apply_template,
)
from envault.vault import VaultError, list_variables


@click.group(name="template")
def templates_group():
    """Manage variable templates."""


@templates_group.command(name="save")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
def cmd_template_save(name, keys):
    """Save a named template with the given variable KEYS."""
    try:
        save_template(name, list(keys))
        click.echo(f"Template '{name}' saved with {len(keys)} key(s).")
    except TemplateError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@templates_group.command(name="delete")
@click.argument("name")
def cmd_template_delete(name):
    """Delete a named template."""
    try:
        delete_template(name)
        click.echo(f"Template '{name}' deleted.")
    except TemplateError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@templates_group.command(name="list")
def cmd_template_list():
    """List all saved templates."""
    templates = list_templates()
    if not templates:
        click.echo("No templates saved.")
        return
    for name, keys in templates.items():
        click.echo(f"{name}: {', '.join(keys)}")


@templates_group.command(name="apply")
@click.argument("name")
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def cmd_template_apply(name, password):
    """Check vault coverage for a template."""
    try:
        vault_keys = list(list_variables(password).keys())
        coverage = apply_template(name, vault_keys)
        all_present = all(coverage.values())
        for key, present in coverage.items():
            status = click.style("OK", fg="green") if present else click.style("MISSING", fg="red")
            click.echo(f"  {key}: {status}")
        if all_present:
            click.echo("All template keys are present in the vault.")
        else:
            missing = [k for k, v in coverage.items() if not v]
            click.echo(f"{len(missing)} key(s) missing from vault.", err=True)
            raise SystemExit(1)
    except (TemplateError, VaultError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
