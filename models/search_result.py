from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchResult:
    source_type: str
    source_id: int
    title: str
    subtitle: str
    content_preview: str
    tags_text: str = ""

    @property
    def display_text(self) -> str:
        if self.tags_text:
            return f"[{self.source_type}] {self.title} | {self.tags_text}"
        return f"[{self.source_type}] {self.title}"
