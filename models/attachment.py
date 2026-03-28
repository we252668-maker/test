from __future__ import annotations

from dataclasses import dataclass

from models.base_model import BaseModel


@dataclass
class Attachment(BaseModel):
    owner_type: str = ""
    owner_id: int | None = None
    file_name: str = ""
    stored_path: str = ""
    mime_type: str = ""
    file_size: int = 0
    checksum: str = ""
    created_by: int | None = None
    created_at: str = ""
