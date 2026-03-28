from __future__ import annotations

from dataclasses import dataclass

from models.base_model import BaseModel


@dataclass
class SearchDocument(BaseModel):
    source_type: str = ""
    source_id: int | None = None
    title: str = ""
    content: str = ""
    tags_text: str = ""
    owner_id: int | None = None
    updated_at: str = ""
