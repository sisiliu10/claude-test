from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from social.calendar import display_calendar, display_entry_detail
from social.generator import GenerationError, generate_content, regenerate_content
from social.models import ContentEntry, ContentStatus, Platform
from social.platforms import list_platforms
from social.store import ContentStore, EntryNotFoundError

console = Console()
store = ContentStore()

PLATFORM_CHOICES = click.Choice([p.value for p in Platform])
STATUS_CHOICES = click.Choice([s.value for s in ContentStatus])


@click.group()
@click.version_option(package_name="social-content")
def cli():
    """Social - AI-powered social media content creation tool."""
    pass


@cli.command()
@click.option("--platform", "-p", type=PLATFORM_CHOICES, prompt="Target platform")
@click.option("--topic", "-t", prompt="Content topic")
@click.option("--schedule", "-s", default=None, help="Schedule date (YYYY-MM-DD).")
@click.option("--save/--no-save", default=True, help="Save generated content.")
def generate(platform, topic, schedule, save):
    """Generate AI-powered content for a social media platform."""
    plat = Platform(platform)
    console.print(f"\n[bold]Generating {platform} content about:[/bold] {topic}\n")

    with console.status("Generating content..."):
        try:
            content = generate_content(topic, plat)
        except GenerationError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise SystemExit(1)

    console.print(f"[green]Generated content:[/green]\n")
    console.print(content)
    console.print(f"\n[dim]({len(content)} characters)[/dim]\n")

    if save:
        status = ContentStatus.SCHEDULED if schedule else ContentStatus.DRAFT
        entry = ContentEntry.new(
            platform=plat,
            content=content,
            topic=topic,
            scheduled_date=schedule,
            status=status,
        )
        store.add_entry(entry)
        console.print(f"[green]Saved[/green] with ID: [bold]{entry.id}[/bold]")

    if click.confirm("Regenerate?", default=False):
        feedback = click.prompt("Feedback (optional)", default="", show_default=False)
        with console.status("Regenerating..."):
            try:
                entry_obj = ContentEntry.new(platform=plat, content=content, topic=topic)
                new_content = regenerate_content(entry_obj, feedback)
            except GenerationError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise SystemExit(1)

        console.print(f"\n[green]Regenerated content:[/green]\n")
        console.print(new_content)
        console.print(f"\n[dim]({len(new_content)} characters)[/dim]\n")

        if save and click.confirm("Save this version?", default=True):
            new_entry = ContentEntry.new(
                platform=plat,
                content=new_content,
                topic=topic,
                scheduled_date=schedule,
                status=ContentStatus.SCHEDULED if schedule else ContentStatus.DRAFT,
            )
            store.add_entry(new_entry)
            console.print(f"[green]Saved[/green] with ID: [bold]{new_entry.id}[/bold]")


@cli.group(invoke_without_command=True)
@click.option("--platform", "-p", type=PLATFORM_CHOICES, default=None)
@click.option("--status", type=STATUS_CHOICES, default=None)
@click.option("--week", "-w", is_flag=True, help="Show week view.")
@click.pass_context
def calendar(ctx, platform, status, week):
    """View and manage the content calendar."""
    if ctx.invoked_subcommand is None:
        plat = Platform(platform) if platform else None
        stat = ContentStatus(status) if status else None
        display_calendar(store, platform=plat, status=stat, week=week, console=console)


@calendar.command("add")
@click.option("--platform", "-p", type=PLATFORM_CHOICES, prompt="Platform")
@click.option("--content", "-c", prompt="Content text")
@click.option("--topic", "-t", prompt="Topic")
@click.option("--schedule", "-s", default=None, help="Schedule date (YYYY-MM-DD).")
@click.option("--status", default="draft", type=STATUS_CHOICES)
def calendar_add(platform, content, topic, schedule, status):
    """Manually add content to the calendar."""
    entry = ContentEntry.new(
        platform=Platform(platform),
        content=content,
        topic=topic,
        scheduled_date=schedule,
        status=ContentStatus(status),
    )
    store.add_entry(entry)
    console.print(f"[green]Added[/green] entry [bold]{entry.id}[/bold]")
    display_entry_detail(entry, console=console)


@cli.command()
def platforms():
    """List supported platforms and their constraints."""
    table = Table(title="Supported Platforms")
    table.add_column("Platform", style="bold")
    table.add_column("Max Length", justify="right")
    table.add_column("Tone")
    table.add_column("Hashtags")

    for config in list_platforms():
        table.add_row(
            config.name,
            str(config.max_length),
            config.tone,
            config.hashtag_style,
        )

    console.print(table)


@cli.command()
@click.argument("entry_id")
@click.option("--content", "-c", default=None, help="New content text.")
@click.option("--schedule", "-s", default=None, help="New schedule date (YYYY-MM-DD).")
@click.option("--status", default=None, type=STATUS_CHOICES)
@click.option("--regenerate", "-r", is_flag=True, help="Regenerate content using AI.")
def edit(entry_id, content, schedule, status, regenerate):
    """Edit an existing content entry."""
    entry = store.get_entry(entry_id)
    if entry is None:
        console.print(f"[red]Entry not found:[/red] {entry_id}")
        raise SystemExit(1)

    if regenerate:
        feedback = click.prompt("Feedback for regeneration (optional)", default="", show_default=False)
        with console.status("Regenerating..."):
            try:
                new_content = regenerate_content(entry, feedback)
            except GenerationError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise SystemExit(1)
        console.print(f"\n[green]Regenerated:[/green]\n{new_content}\n")
        if click.confirm("Use this version?", default=True):
            content = new_content
        else:
            console.print("[dim]Keeping original content.[/dim]")
            return

    kwargs = {}
    if content is not None:
        kwargs["content"] = content
    if schedule is not None:
        kwargs["scheduled_date"] = schedule
    if status is not None:
        kwargs["status"] = ContentStatus(status)

    if not kwargs:
        console.print("[dim]No changes specified.[/dim]")
        display_entry_detail(entry, console=console)
        return

    try:
        updated = store.update_entry(entry.id, **kwargs)
    except EntryNotFoundError:
        console.print(f"[red]Entry not found:[/red] {entry_id}")
        raise SystemExit(1)

    console.print("[green]Updated![/green]")
    display_entry_detail(updated, console=console)


@cli.command()
@click.argument("entry_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation.")
def delete(entry_id, force):
    """Delete a content entry from the calendar."""
    entry = store.get_entry(entry_id)
    if entry is None:
        console.print(f"[red]Entry not found:[/red] {entry_id}")
        raise SystemExit(1)

    display_entry_detail(entry, console=console)

    if not force and not click.confirm("Delete this entry?", default=False):
        console.print("[dim]Cancelled.[/dim]")
        return

    try:
        store.delete_entry(entry.id)
    except EntryNotFoundError:
        console.print(f"[red]Entry not found:[/red] {entry_id}")
        raise SystemExit(1)

    console.print(f"[green]Deleted[/green] entry [bold]{entry.id}[/bold]")
