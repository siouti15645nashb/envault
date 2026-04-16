import click
from envault.env_schema import (
    define_field, remove_field, get_schema, validate_vault, SchemaError
)


@click.group(name="schema")
def schema_group():
    """Manage environment variable schema definitions."""
    pass


@schema_group.command(name="define")
@click.argument("key")
@click.option("--required/--optional", default=True, help="Mark field as required or optional.")
@click.option("--pattern", default=None, help="Regex pattern the value must match.")
@click.option("--description", default="", help="Human-readable description.")
@click.argument("vault_path", default=".envault")
def cmd_schema_define(key, required, pattern, description, vault_path):
    """Define or update a schema field."""
    try:
        define_field(vault_path, key, required=required, pattern=pattern, description=description)
        click.echo(f"Schema field '{key}' defined.")
    except SchemaError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schema_group.command(name="remove")
@click.argument("key")
@click.argument("vault_path", default=".envault")
def cmd_schema_remove(key, vault_path):
    """Remove a schema field definition."""
    try:
        remove_field(vault_path, key)
        click.echo(f"Schema field '{key}' removed.")
    except SchemaError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schema_group.command(name="list")
@click.argument("vault_path", default=".envault")
def cmd_schema_list(vault_path):
    """List all schema field definitions."""
    schema = get_schema(vault_path)
    if not schema:
        click.echo("No schema fields defined.")
        return
    for key, meta in schema.items():
        req = "required" if meta.get("required") else "optional"
        pattern = f", pattern={meta['pattern']}" if meta.get("pattern") else ""
        desc = f" — {meta['description']}" if meta.get("description") else ""
        click.echo(f"  {key} [{req}{pattern}]{desc}")


@schema_group.command(name="validate")
@click.argument("vault_path", default=".envault")
@click.argument("password")
def cmd_schema_validate(vault_path, password):
    """Validate vault variables against the schema."""
    try:
        issues = validate_vault(vault_path, password)
        if not issues:
            click.echo("Vault validates against schema.")
            return
        for issue in issues:
            click.echo(f"  [{issue.severity.upper()}] {issue.key}: {issue.message}")
        raise SystemExit(1)
    except SchemaError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
