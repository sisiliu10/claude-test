from __future__ import annotations

from datetime import date, timedelta
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from social.models import ContentEntry, ContentStatus, Platform
from social.store import ContentStore

STATUS_COLORS = {
    ContentStatus.DRAFT: "yellow",
    ContentStatus.SCHEDULED: "blue",
    ContentStatus.PUBLISHED: "green",
}


def _truncate(text: str, max_len: int = 40) -> str:
    text = text.replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def render_calendar_table(
    entries: List[ContentEntry], title: str = "Content Calendar"
) -> Table:
    table = Table(title=title, show_lines=False)
    table.add_column("ID", style="dim", width=10)
    table.add_column("Platform", width=12)
    table.add_column("Status", width=11)
    table.add_column("Scheduled", width=12)
    table.add_column("Topic / Preview", min_width=30)

    for entry in entries:
        color = STATUS_COLORS.get(entry.status, "white")
        status_text = Text(entry.status.value, style=color)
        scheduled = entry.scheduled_date or "--"
        preview = _truncate(f"{entry.topic}: {entry.content}")
        table.add_row(entry.id, entry.platform.value.title(), status_text, scheduled, preview)

    return table


def render_week_view(
    entries: List[ContentEntry], start_date: Optional[date] = None
) -> Table:
    if start_date is None:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # Monday

    table = Table(title=f"Week of {start_date.isoformat()}", show_lines=True)

    days = []
    for i in range(7):
        d = start_date + timedelta(days=i)
        day_name = d.strftime("%a %m/%d")
        table.add_column(day_name, width=20)
        days.append(d.isoformat())

    # Group entries by scheduled date
    by_date = {}
    for entry in entries:
        if entry.scheduled_date and entry.scheduled_date in days:
            by_date.setdefault(entry.scheduled_date, []).append(entry)

    # Build row cells
    max_rows = max((len(v) for v in by_date.values()), default=0)
    for row_idx in range(max(max_rows, 1)):
        cells = []
        for day_iso in days:
            day_entries = by_date.get(day_iso, [])
            if row_idx < len(day_entries):
                e = day_entries[row_idx]
                color = STATUS_COLORS.get(e.status, "white")
                cells.append(f"[{color}]{e.platform.value.title()}[/{color}]\n{_truncate(e.topic, 16)}")
            else:
                cells.append("")
        table.add_row(*cells)

    return table


def display_entry_detail(entry: ContentEntry, console: Optional[Console] = None) -> None:
    if console is None:
        console = Console()

    color = STATUS_COLORS.get(entry.status, "white")
    content = (
        f"[bold]ID:[/bold] {entry.id}\n"
        f"[bold]Platform:[/bold] {entry.platform.value.title()}\n"
        f"[bold]Status:[/bold] [{color}]{entry.status.value}[/{color}]\n"
        f"[bold]Topic:[/bold] {entry.topic}\n"
        f"[bold]Scheduled:[/bold] {entry.scheduled_date or 'Not scheduled'}\n"
        f"[bold]Created:[/bold] {entry.created_at}\n"
        f"\n[bold]Content:[/bold]\n{entry.content}"
    )
    console.print(Panel(content, title="Content Entry", border_style=color))


def display_calendar(
    store: ContentStore,
    platform: Optional[Platform] = None,
    status: Optional[ContentStatus] = None,
    week: bool = False,
    console: Optional[Console] = None,
) -> None:
    if console is None:
        console = Console()

    entries = store.list_entries(platform=platform, status=status)

    if not entries:
        console.print("[dim]No content entries found.[/dim]")
        return

    if week:
        table = render_week_view(entries)
    else:
        table = render_calendar_table(entries)

    console.print(table)
