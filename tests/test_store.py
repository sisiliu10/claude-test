import json

import pytest

from social.models import ContentEntry, ContentStatus, Platform
from social.store import ContentStore, EntryNotFoundError


@pytest.fixture
def store(tmp_path):
    return ContentStore(path=tmp_path / "content.json")


def _make_entry(**kwargs):
    defaults = dict(platform=Platform.TWITTER, content="Hello", topic="test")
    defaults.update(kwargs)
    return ContentEntry.new(**defaults)


def test_add_and_retrieve(store):
    entry = _make_entry()
    store.add_entry(entry)
    result = store.get_entry(entry.id)
    assert result is not None
    assert result.id == entry.id
    assert result.content == "Hello"


def test_list_empty_store(store):
    assert store.list_entries() == []


def test_list_entries(store):
    store.add_entry(_make_entry(content="a"))
    store.add_entry(_make_entry(content="b"))
    assert len(store.list_entries()) == 2


def test_list_filter_by_platform(store):
    store.add_entry(_make_entry(platform=Platform.TWITTER))
    store.add_entry(_make_entry(platform=Platform.LINKEDIN))
    results = store.list_entries(platform=Platform.TWITTER)
    assert len(results) == 1
    assert results[0].platform == Platform.TWITTER


def test_list_filter_by_status(store):
    store.add_entry(_make_entry(status=ContentStatus.DRAFT))
    store.add_entry(_make_entry(status=ContentStatus.SCHEDULED))
    results = store.list_entries(status=ContentStatus.DRAFT)
    assert len(results) == 1
    assert results[0].status == ContentStatus.DRAFT


def test_update_entry(store):
    entry = _make_entry()
    store.add_entry(entry)
    updated = store.update_entry(entry.id, content="Updated!", status=ContentStatus.SCHEDULED)
    assert updated.content == "Updated!"
    assert updated.status == ContentStatus.SCHEDULED
    # Verify persistence
    fetched = store.get_entry(entry.id)
    assert fetched.content == "Updated!"


def test_update_nonexistent_raises(store):
    with pytest.raises(EntryNotFoundError):
        store.update_entry("nonexistent", content="x")


def test_delete_entry(store):
    entry = _make_entry()
    store.add_entry(entry)
    deleted = store.delete_entry(entry.id)
    assert deleted.id == entry.id
    assert store.get_entry(entry.id) is None


def test_delete_nonexistent_raises(store):
    with pytest.raises(EntryNotFoundError):
        store.delete_entry("nonexistent")


def test_id_prefix_matching(store):
    entry = _make_entry()
    store.add_entry(entry)
    prefix = entry.id[:4]
    result = store.get_entry(prefix)
    assert result is not None
    assert result.id == entry.id


def test_json_file_format(store, tmp_path):
    entry = _make_entry()
    store.add_entry(entry)
    with open(tmp_path / "content.json") as f:
        data = json.load(f)
    assert data["version"] == 1
    assert len(data["entries"]) == 1
    assert data["entries"][0]["id"] == entry.id


def test_sorted_by_scheduled_date(store):
    store.add_entry(_make_entry(content="no date"))
    store.add_entry(_make_entry(content="later", scheduled_date="2026-03-01"))
    store.add_entry(_make_entry(content="sooner", scheduled_date="2026-02-01"))
    results = store.list_entries()
    assert results[0].content == "sooner"
    assert results[1].content == "later"
    assert results[2].content == "no date"
