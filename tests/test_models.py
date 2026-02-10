from social.models import ContentEntry, ContentStatus, Platform


def test_platform_values():
    assert Platform.TWITTER.value == "twitter"
    assert Platform.INSTAGRAM.value == "instagram"
    assert Platform.LINKEDIN.value == "linkedin"


def test_content_status_values():
    assert ContentStatus.DRAFT.value == "draft"
    assert ContentStatus.SCHEDULED.value == "scheduled"
    assert ContentStatus.PUBLISHED.value == "published"


def test_content_entry_new_generates_id():
    entry = ContentEntry.new(
        platform=Platform.TWITTER,
        content="Test tweet",
        topic="testing",
    )
    assert len(entry.id) == 8
    assert entry.platform == Platform.TWITTER
    assert entry.content == "Test tweet"
    assert entry.topic == "testing"
    assert entry.status == ContentStatus.DRAFT
    assert entry.scheduled_date is None
    assert entry.created_at is not None


def test_content_entry_new_unique_ids():
    entry1 = ContentEntry.new(Platform.TWITTER, "a", "t")
    entry2 = ContentEntry.new(Platform.TWITTER, "b", "t")
    assert entry1.id != entry2.id


def test_content_entry_new_with_schedule():
    entry = ContentEntry.new(
        platform=Platform.LINKEDIN,
        content="Professional post",
        topic="career",
        scheduled_date="2026-02-14",
        status=ContentStatus.SCHEDULED,
    )
    assert entry.scheduled_date == "2026-02-14"
    assert entry.status == ContentStatus.SCHEDULED


def test_serialization_roundtrip():
    entry = ContentEntry.new(
        platform=Platform.INSTAGRAM,
        content="Check this out!",
        topic="photography",
        scheduled_date="2026-03-01",
    )
    data = entry.to_dict()
    restored = ContentEntry.from_dict(data)

    assert restored.id == entry.id
    assert restored.platform == entry.platform
    assert restored.content == entry.content
    assert restored.topic == entry.topic
    assert restored.created_at == entry.created_at
    assert restored.scheduled_date == entry.scheduled_date
    assert restored.status == entry.status


def test_to_dict_uses_string_values():
    entry = ContentEntry.new(Platform.TWITTER, "test", "topic")
    data = entry.to_dict()
    assert data["platform"] == "twitter"
    assert data["status"] == "draft"
    assert isinstance(data["id"], str)
