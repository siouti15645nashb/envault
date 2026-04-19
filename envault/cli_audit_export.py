"""CLI commands for exporting audit logs."""
import click
from envault.env_audit_export import export_audit_log, export_audit_log_to_file, SUPPORTED_FORMATS, AuditExportError


@click.group("audit-export")
def audit_export_group():
    """Export audit log to a file or stdout."""
    pass


@audit_export_group.command("run")
@click.argument("vault_dir")
@click.option("--format", "fmt", default="json", show_default=True,
              type=click.Choice(SUPPORTED_FORMATS), help="Output format.")
@click.option("--output", "-o", default=None, help="Write to file instead of stdout.")
def cmd_audit_export_run(vault_dir, fmt, output):
    """Export the audit log for VAULT_DIR."""
    try:
        if output:
            count = export_audit_log_to_file(vault_dir, output, fmt)
            click.echo(f"Exported {count} entries to {output} [{fmt}]")
        else:
            content = export_audit_log(vault_dir, fmt)
            click.echo(content)
    except AuditExportError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@audit_export_group.command("formats")
def cmd_audit_export_formats():
    """List supported export formats."""
    for fmt in SUPPORTED_FORMATS:
        click.echo(fmt)
