"""CLI commands for variable quality ratings."""
import click
from envault.env_rating import (
    RatingError,
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
)


@click.group(name="rating")
def rating_group():
    """Manage variable quality ratings (1-5)."""


@rating_group.command(name="set")
@click.argument("key")
@click.argument("rating", type=int)
@click.option("--vault", default=".envault", show_default=True)
def cmd_rating_set(key, rating, vault):
    """Set a quality rating (1-5) for a variable."""
    try:
        set_rating(vault, key, rating)
        click.echo(f"Rating for '{key}' set to {rating}.")
    except RatingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rating_group.command(name="get")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_rating_get(key, vault):
    """Get the quality rating for a variable."""
    r = get_rating(vault, key)
    if r is None:
        click.echo(f"No rating set for '{key}'.")
    else:
        click.echo(f"{key}: {r}/5")


@rating_group.command(name="remove")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def cmd_rating_remove(key, vault):
    """Remove the rating for a variable."""
    try:
        remove_rating(vault, key)
        click.echo(f"Rating for '{key}' removed.")
    except RatingError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@rating_group.command(name="list")
@click.option("--vault", default=".envault", show_default=True)
def cmd_rating_list(vault):
    """List all variable ratings."""
    ratings = list_ratings(vault)
    if not ratings:
        click.echo("No ratings set.")
        return
    for key, r in sorted(ratings.items()):
        click.echo(f"{key}: {r}/5")
