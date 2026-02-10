from unittest.mock import MagicMock

import pytest

from social.generator import (
    GenerationError,
    build_prompt,
    generate_content,
    regenerate_content,
)
from social.models import ContentEntry, Platform
from social.platforms import get_platform_config


def test_build_prompt_includes_platform_constraints():
    config = get_platform_config(Platform.TWITTER)
    prompt = build_prompt("Python tips", config)
    assert "Twitter / X" in prompt
    assert "280" in prompt
    assert "concise and engaging" in prompt
    assert "Python tips" in prompt


def test_build_prompt_includes_extra_instructions():
    config = get_platform_config(Platform.LINKEDIN)
    prompt = build_prompt("AI trends", config, extra="Include statistics")
    assert "Include statistics" in prompt


def _mock_response(text):
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


def test_generate_content(mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response("Generated tweet! #Python")
    mocker.patch("social.generator.anthropic.Anthropic", return_value=mock_client)

    result = generate_content("Python tips", Platform.TWITTER)
    assert result == "Generated tweet! #Python"

    # Verify API was called with correct params
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["max_tokens"] == 1024
    assert "user" in call_kwargs["messages"][0]["role"]


def test_generate_content_retries_on_length(mocker):
    long_text = "x" * 300  # Exceeds Twitter's 280 limit
    short_text = "Short tweet! #Python"

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [
        _mock_response(long_text),
        _mock_response(short_text),
    ]
    mocker.patch("social.generator.anthropic.Anthropic", return_value=mock_client)

    result = generate_content("Python tips", Platform.TWITTER)
    assert result == short_text
    assert mock_client.messages.create.call_count == 2


def test_generate_content_auth_error(mocker):
    import anthropic as anthropic_mod

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic_mod.AuthenticationError(
        message="Invalid API key",
        response=MagicMock(status_code=401),
        body={"error": {"message": "Invalid API key"}},
    )
    mocker.patch("social.generator.anthropic.Anthropic", return_value=mock_client)

    with pytest.raises(GenerationError, match="API key not set"):
        generate_content("test", Platform.TWITTER)


def test_regenerate_content_includes_feedback(mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response("New version")
    mocker.patch("social.generator.anthropic.Anthropic", return_value=mock_client)

    entry = ContentEntry.new(
        platform=Platform.TWITTER, content="Old tweet", topic="Python"
    )
    result = regenerate_content(entry, feedback="Make it funnier")
    assert result == "New version"

    call_kwargs = mock_client.messages.create.call_args.kwargs
    user_msg = call_kwargs["messages"][0]["content"]
    assert "Make it funnier" in user_msg
    assert "Old tweet" in user_msg
