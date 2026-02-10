from __future__ import annotations

import os

import anthropic

from social.models import ContentEntry, Platform
from social.platforms import PlatformConfig, get_platform_config


DEFAULT_MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = (
    "You are an expert social media content creator. You write platform-specific "
    "content that is engaging, on-brand, and optimized for each platform's audience "
    "and format conventions. Write ONLY the post content. Do not include explanations, "
    "alternatives, or meta-commentary. The output should be ready to copy-paste."
)


class GenerationError(Exception):
    pass


def _get_model() -> str:
    return os.environ.get("SOCIAL_MODEL", DEFAULT_MODEL)


def build_prompt(topic: str, config: PlatformConfig, extra: str = "") -> str:
    prompt = (
        f"Create a {config.name} post about the following topic:\n\n"
        f"Topic: {topic}\n\n"
        f"Platform constraints:\n"
        f"- Maximum length: {config.max_length} characters\n"
        f"- Tone: {config.tone}\n"
        f"- Hashtag style: {config.hashtag_style}\n"
        f"- Format description: {config.description}\n\n"
        f"Example format:\n{config.example_format}"
    )
    if extra:
        prompt += f"\n\nAdditional instructions: {extra}"
    return prompt


def generate_content(
    topic: str,
    platform: Platform,
    extra: str = "",
) -> str:
    config = get_platform_config(platform)
    user_prompt = build_prompt(topic, config, extra)

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=_get_model(),
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except anthropic.AuthenticationError:
        raise GenerationError(
            "API key not set or invalid. "
            "Set your key: export ANTHROPIC_API_KEY=sk-ant-..."
        )
    except anthropic.APIError as e:
        raise GenerationError(f"API error: {e}")

    content = response.content[0].text

    # If content exceeds platform limit, retry once asking for shorter version
    if len(content) > config.max_length:
        try:
            retry_prompt = (
                f"The previous response was {len(content)} characters. "
                f"It MUST be under {config.max_length} characters. "
                f"Rewrite it shorter while keeping the key message:\n\n{content}"
            )
            response = client.messages.create(
                model=_get_model(),
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": retry_prompt}],
            )
            content = response.content[0].text
        except anthropic.APIError:
            pass  # Return the original content with a length warning

    return content


def regenerate_content(
    original: ContentEntry,
    feedback: str = "",
) -> str:
    config = get_platform_config(original.platform)
    extra = ""
    if feedback:
        extra = f"The previous version was:\n{original.content}\n\nFeedback: {feedback}"
    return generate_content(original.topic, original.platform, extra)
