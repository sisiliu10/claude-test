from io import StringIO

from rich.console import Console

from social.calendar import (
    display_calendar,
    display_entry_detail,
    render_calendar_table,
    render_week_view,
)
from social.models import ContentEntry, ContentStatus, Platform
from social.store import ContentStore


def _make_entry(**kwargs):
    defaults = dict(platform=Platform.TWITTER, content="Hello world", topic="test")
    defaults.update(kwargs)
    return ContentEntry.new(**defaults)


def _capture_output(fn, *args, **kwargs):
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, width=120)
    fn(*args, console=console, **kwargs)
    return buf.getvalue()


def test_render_calendar_table_columns():
    entries = [_make_entry(), _make_entry(platform=Platform.LINKEDIN)]
    table = render_calendar_table(entries)
    assert table.title == "Content Calendar"
    assert len(table.columns) == 5
    assert table.row_count == 2


def test_render_calendar_table_empty():
    table = render_calendar_table([])
    assert table.row_count == 0


def test_render_week_view():
    from datetime import date

    entry = _make_entry(scheduled_date="2026-02-09")
    table = render_week_view([entry], start_date=date(2026, 2, 9))
    assert len(table.columns) == 7


def test_display_entry_detail():
    entry = _make_entry(content="Full content here")
    output = _capture_output(display_entry_detail, entry)
    assert "Full content here" in output
    assert entry.id in output


def test_display_calendar_empty(tmp_path):
    store = ContentStore(path=tmp_path / "content.json")
    output = _capture_output(display_calendar, store)
    assert "No content entries found" in output


def test_display_calendar_with_entries(tmp_path):
    store = ContentStore(path=tmp_path / "content.json")
    store.add_entry(_make_entry(topic="Python tips"))
    output = _capture_output(display_calendar, store)
    assert "Python tips" in output
