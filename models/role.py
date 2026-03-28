from __future__ import annotations

from dataclasses import dataclass, field

from models.base_model import BaseModel


@dataclass
class Role(BaseModel):
    code: str = ""
    name: str = ""
    description: str = ""
    permissions: list[str] = field(default_factory=list)
