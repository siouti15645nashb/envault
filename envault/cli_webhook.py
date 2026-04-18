import click
from envault.env_webhook import (
    WebhookError,
    add_webhook,
    remove_webhook,
    list_webhooks,
    get_webhook,
)

DEFAULT_VAULT = ".envault"


@click.group("webhook")
def webhook_group():
    """Manage webhooks for vault event notifications."""


@webhook_group.command("add")
@click.argument("name")
@click.argument("url")
@click.option("--events", default="set,delete,rotate", help="Comma-separated event list.")
@click.option("--vault", default=DEFAULT_VAULT)
def cmd_webhook_add(name, url, events, vault):
    """Register a webhook URL for vault events."""
    event_list = [e.strip() for e in events.split(",") if e.strip()]
    try:
        add_webhook(vault, name, url, event_list)
        click.echo(f"Webhook '{name}' added for events: {', '.join(event_list)}")
    except WebhookError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@webhook_group.command("remove")
@click.argument("name")
@click.option("--vault", default=DEFAULT_VAULT)
def cmd_webhook_remove(name, vault):
    """Remove a registered webhook."""
    try:
        remove_webhook(vault, name)
        click.echo(f"Webhook '{name}' removed.")
    except WebhookError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@webhook_group.command("list")
@click.option("--vault", default=DEFAULT_VAULT)
def cmd_webhook_list(vault):
    """List all registered webhooks."""
    hooks = list_webhooks(vault)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for name, info in hooks.items():
        click.echo(f"{name}: {info['url']} (events: {', '.join(info['events'])})")


@webhook_group.command("get")
@click.argument("name")
@click.option("--vault", default=DEFAULT_VAULT)
def cmd_webhook_get(name, vault):
    """Show details for a specific webhook."""
    try:
        info = get_webhook(vault, name)
        click.echo(f"URL: {info['url']}")
        click.echo(f"Events: {', '.join(info['events'])}")
    except WebhookError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
