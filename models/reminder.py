from __future__ import annotations

from dataclasses import dataclass

from models.base_model import BaseModel


@dataclass
class Reminder(BaseModel):
    title: str = ""
    category: str = ""
    description: str = ""
    due_at: str = ""
    priority: int = 0
    status: str = "pending"
    discord_creation_notice_sent_at: str = ""
    discord_due_notice_sent_at: str = ""
    last_discord_error: str = ""
    created_at: str = ""
    updated_at: str = ""
