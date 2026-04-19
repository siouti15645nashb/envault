import click
from envault.env_approval import (
    ApprovalError,
    request_approval,
    review_approval,
    get_approval,
    list_approvals,
    remove_approval,
)


@click.group(name="approval")
def approval_group():
    """Manage change approval requests for vault variables."""


@approval_group.command(name="request")
@click.argument("key")
@click.argument("requester")
@click.argument("vault_dir", default=".")
def cmd_approval_request(key, requester, vault_dir):
    """Request approval for a variable change."""
    try:
        entry = request_approval(vault_dir, key, requester)
        click.echo(f"Approval requested for '{key}' by {requester} (status: {entry['status']})")
    except ApprovalError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@approval_group.command(name="review")
@click.argument("key")
@click.argument("reviewer")
@click.argument("status")
@click.argument("vault_dir", default=".")
def cmd_approval_review(key, reviewer, status, vault_dir):
    """Approve or reject a pending approval request."""
    try:
        entry = review_approval(vault_dir, key, reviewer, status)
        click.echo(f"Approval for '{key}' set to '{entry['status']}' by {reviewer}")
    except ApprovalError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@approval_group.command(name="get")
@click.argument("key")
@click.argument("vault_dir", default=".")
def cmd_approval_get(key, vault_dir):
    """Show approval status for a variable."""
    entry = get_approval(vault_dir, key)
    if entry is None:
        click.echo(f"No approval record for '{key}'")
    else:
        click.echo(f"{key}: status={entry['status']}, requester={entry['requester']}, reviewed_by={entry['reviewed_by']}")


@approval_group.command(name="list")
@click.option("--status", default=None, help="Filter by status (pending/approved/rejected)")
@click.argument("vault_dir", default=".")
def cmd_approval_list(status, vault_dir):
    """List all approval requests."""
    records = list_approvals(vault_dir, status=status)
    if not records:
        click.echo("No approval records found.")
    else:
        for key, entry in records.items():
            click.echo(f"{key}: {entry['status']} (by {entry['requester']})")


@approval_group.command(name="remove")
@click.argument("key")
@click.argument("vault_dir", default=".")
def cmd_approval_remove(key, vault_dir):
    """Remove an approval record."""
    try:
        remove_approval(vault_dir, key)
        click.echo(f"Approval record for '{key}' removed.")
    except ApprovalError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
