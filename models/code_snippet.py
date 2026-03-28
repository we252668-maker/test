from __future__ import annotations

from dataclasses import dataclass, field

from models.base_model import BaseModel


@dataclass
class CodeSnippet(BaseModel):
    title: str = ""
    language: str = "python"
    code: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    @property
    def tag_text(self) -> str:
        return ", ".join(self.tags)
