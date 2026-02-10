from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Platform(str, Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


@dataclass
class ContentEntry:
    id: str
    platform: Platform
    content: str
    topic: str
    created_at: str
    scheduled_date: Optional[str]
    status: ContentStatus

    @staticmethod
    def new(
        platform: Platform,
        content: str,
        topic: str,
        scheduled_date: Optional[str] = None,
        status: ContentStatus = ContentStatus.DRAFT,
    ) -> ContentEntry:
        return ContentEntry(
            id=uuid.uuid4().hex[:8],
            platform=platform,
            content=content,
            topic=topic,
            created_at=datetime.now().isoformat(),
            scheduled_date=scheduled_date,
            status=status,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform.value,
            "content": self.content,
            "topic": self.topic,
            "created_at": self.created_at,
            "scheduled_date": self.scheduled_date,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ContentEntry:
        return cls(
            id=data["id"],
            platform=Platform(data["platform"]),
            content=data["content"],
            topic=data["topic"],
            created_at=data["created_at"],
            scheduled_date=data.get("scheduled_date"),
            status=ContentStatus(data["status"]),
        )
