from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from social.models import Platform


@dataclass(frozen=True)
class PlatformConfig:
    name: str
    platform: Platform
    max_length: int
    description: str
    hashtag_style: str
    tone: str
    example_format: str


PLATFORMS: Dict[Platform, PlatformConfig] = {
    Platform.TWITTER: PlatformConfig(
        name="Twitter / X",
        platform=Platform.TWITTER,
        max_length=280,
        description="Short-form microblogging. Punchy, engaging, concise.",
        hashtag_style="inline",
        tone="concise and engaging, sometimes witty",
        example_format="Main point in 1-2 sentences. #Hashtag #Topic",
    ),
    Platform.INSTAGRAM: PlatformConfig(
        name="Instagram",
        platform=Platform.INSTAGRAM,
        max_length=2200,
        description="Visual-first platform. Captions support storytelling with emoji and hashtag blocks.",
        hashtag_style="footer",
        tone="casual, relatable, storytelling-oriented with emoji",
        example_format=(
            "Opening hook line\n\n"
            "Body paragraph with details and personality.\n\n"
            "Call to action\n\n"
            "#hashtag1 #hashtag2 #hashtag3"
        ),
    ),
    Platform.LINKEDIN: PlatformConfig(
        name="LinkedIn",
        platform=Platform.LINKEDIN,
        max_length=3000,
        description="Professional networking. Thought leadership, industry insights, career content.",
        hashtag_style="footer",
        tone="professional, insightful, thought-leadership",
        example_format=(
            "Attention-grabbing opening line.\n\n"
            "Supporting paragraph with data or experience.\n\n"
            "Key takeaway or call to discussion.\n\n"
            "#Industry #Topic"
        ),
    ),
}


def get_platform_config(platform: Platform) -> PlatformConfig:
    return PLATFORMS[platform]


def list_platforms() -> List[PlatformConfig]:
    return list(PLATFORMS.values())
