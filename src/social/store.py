from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional

from social.models import ContentEntry, ContentStatus, Platform


DEFAULT_STORE_PATH = Path.home() / ".social-content" / "content.json"


class EntryNotFoundError(ValueError):
    pass


class ContentStore:
    def __init__(self, path: Path = DEFAULT_STORE_PATH):
        self.path = path

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self) -> List[dict]:
        self._ensure_file()
        with open(self.path, "r") as f:
            data = json.load(f)
        return data.get("entries", [])

    def _save(self, entries: List[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"version": 1, "entries": entries}
        # Atomic write: write to temp file then rename
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.path.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, str(self.path))
        except Exception:
            os.unlink(tmp_path)
            raise

    def list_entries(
        self,
        platform: Optional[Platform] = None,
        status: Optional[ContentStatus] = None,
    ) -> List[ContentEntry]:
        raw = self._load()
        entries = [ContentEntry.from_dict(e) for e in raw]

        if platform is not None:
            entries = [e for e in entries if e.platform == platform]
        if status is not None:
            entries = [e for e in entries if e.status == status]

        # Sort: scheduled entries first (by date), then unscheduled (by created_at)
        def sort_key(e: ContentEntry):
            if e.scheduled_date:
                return (0, e.scheduled_date)
            return (1, e.created_at)

        entries.sort(key=sort_key)
        return entries

    def get_entry(self, entry_id: str) -> Optional[ContentEntry]:
        raw = self._load()
        matches = [
            e for e in raw if e["id"] == entry_id or e["id"].startswith(entry_id)
        ]
        if len(matches) == 1:
            return ContentEntry.from_dict(matches[0])
        return None

    def add_entry(self, entry: ContentEntry) -> ContentEntry:
        raw = self._load()
        raw.append(entry.to_dict())
        self._save(raw)
        return entry

    def update_entry(self, entry_id: str, **kwargs) -> ContentEntry:
        raw = self._load()
        for i, e in enumerate(raw):
            if e["id"] == entry_id or e["id"].startswith(entry_id):
                for key, value in kwargs.items():
                    if key == "platform" and isinstance(value, Platform):
                        e[key] = value.value
                    elif key == "status" and isinstance(value, ContentStatus):
                        e[key] = value.value
                    else:
                        e[key] = value
                self._save(raw)
                return ContentEntry.from_dict(e)
        raise EntryNotFoundError(f"No entry found with ID: {entry_id}")

    def delete_entry(self, entry_id: str) -> ContentEntry:
        raw = self._load()
        for i, e in enumerate(raw):
            if e["id"] == entry_id or e["id"].startswith(entry_id):
                deleted = ContentEntry.from_dict(raw.pop(i))
                self._save(raw)
                return deleted
        raise EntryNotFoundError(f"No entry found with ID: {entry_id}")
