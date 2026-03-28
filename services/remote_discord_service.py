from __future__ import annotations

from models.settings_model import SettingsModel
from services.api_client import ApiClient


class RemoteDiscordService:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def get_settings(self) -> SettingsModel:
        return SettingsModel(discord_webhook_url="[Managed by Render env: DISCORD_WEBHOOK_URL]")

    def save_settings(self, settings: SettingsModel) -> None:
        _ = settings

    def send_test_message(self) -> None:
        self.api_client.post("/test-discord")

    def uses_environment_webhook(self) -> bool:
        return True
