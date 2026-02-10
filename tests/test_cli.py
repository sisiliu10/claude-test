from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from social.cli import cli
from social.models import ContentEntry, ContentStatus, Platform
from social.store import ContentStore


@patch("social.cli.store")
def test_platforms_command(mock_store):
    runner = CliRunner()
    result = runner.invoke(cli, ["platforms"])
    assert result.exit_code == 0
    assert "Twitter" in result.output
    assert "Instagram" in result.output
    assert "LinkedIn" in result.output
    assert "280" in result.output


@patch("social.cli.store")
def test_calendar_empty(mock_store):
    mock_store.list_entries.return_value = []
    runner = CliRunner()
    result = runner.invoke(cli, ["calendar"])
    assert result.exit_code == 0
    assert "No content entries found" in result.output


@patch("social.cli.store")
def test_calendar_with_entries(mock_store):
    entry = ContentEntry.new(Platform.TWITTER, "Test tweet", "testing")
    mock_store.list_entries.return_value = [entry]
    runner = CliRunner()
    result = runner.invoke(cli, ["calendar"])
    assert result.exit_code == 0
    assert "testing" in result.output


@patch("social.cli.store")
def test_calendar_add(mock_store):
    mock_store.add_entry.side_effect = lambda e: e
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["calendar", "add", "-p", "twitter", "-c", "My tweet", "-t", "topic"],
    )
    assert result.exit_code == 0
    assert "Added" in result.output
    mock_store.add_entry.assert_called_once()


@patch("social.cli.store")
def test_generate_command(mock_store):
    mock_store.add_entry.side_effect = lambda e: e

    runner = CliRunner()
    with patch("social.cli.generate_content", return_value="AI generated tweet!"):
        result = runner.invoke(
            cli,
            ["generate", "-p", "twitter", "-t", "Python tips"],
            input="n\n",  # Don't regenerate
        )
    assert result.exit_code == 0
    assert "AI generated tweet!" in result.output
    assert "Saved" in result.output


@patch("social.cli.store")
def test_generate_no_save(mock_store):
    runner = CliRunner()
    with patch("social.cli.generate_content", return_value="Content"):
        result = runner.invoke(
            cli,
            ["generate", "-p", "twitter", "-t", "test", "--no-save"],
            input="n\n",
        )
    assert result.exit_code == 0
    mock_store.add_entry.assert_not_called()


@patch("social.cli.store")
def test_edit_command(mock_store):
    entry = ContentEntry.new(Platform.TWITTER, "Old content", "test")
    mock_store.get_entry.return_value = entry
    mock_store.update_entry.return_value = ContentEntry(
        id=entry.id, platform=entry.platform, content="New content",
        topic=entry.topic, created_at=entry.created_at,
        scheduled_date=None, status=ContentStatus.SCHEDULED,
    )

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["edit", entry.id, "-c", "New content", "--status", "scheduled"],
    )
    assert result.exit_code == 0
    assert "Updated" in result.output


@patch("social.cli.store")
def test_edit_not_found(mock_store):
    mock_store.get_entry.return_value = None
    runner = CliRunner()
    result = runner.invoke(cli, ["edit", "nonexistent", "-c", "test"])
    assert result.exit_code == 1
    assert "not found" in result.output


@patch("social.cli.store")
def test_delete_with_force(mock_store):
    entry = ContentEntry.new(Platform.TWITTER, "Delete me", "test")
    mock_store.get_entry.return_value = entry
    mock_store.delete_entry.return_value = entry

    runner = CliRunner()
    result = runner.invoke(cli, ["delete", entry.id, "--force"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


@patch("social.cli.store")
def test_delete_not_found(mock_store):
    mock_store.get_entry.return_value = None
    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "nonexistent", "--force"])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
