from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SettingsModel:
    discord_webhook_url: str = ""
