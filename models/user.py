from __future__ import annotations

from dataclasses import dataclass

from models.base_model import BaseModel


@dataclass
class User(BaseModel):
    username: str = ""
    display_name: str = ""
    email: str = ""
    password_hash: str = ""
    status: str = "active"
    is_system_admin: bool = False
    created_at: str = ""
    updated_at: str = ""
