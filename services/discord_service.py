from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime

from models.reminder import Reminder
from models.settings_model import SettingsModel


logger = logging.getLogger(__name__)


class DiscordService:
    def __init__(self, connection: sqlite3.Connection, timeout_seconds: int = 10) -> None:
        self.connection = connection
        self.timeout_seconds = timeout_seconds

    def get_settings(self) -> SettingsModel:
        env_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
        if env_webhook_url:
            return SettingsModel(discord_webhook_url=env_webhook_url)

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT discord_webhook_url
            FROM email_settings
            WHERE id = 1
            """
        )
        row = cursor.fetchone()
        if row is None:
            return SettingsModel()
        return SettingsModel(discord_webhook_url=row["discord_webhook_url"])

    def save_settings(self, settings: SettingsModel) -> None:
        if self.uses_environment_webhook():
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO email_settings (id, discord_webhook_url, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                discord_webhook_url = excluded.discord_webhook_url,
                updated_at = excluded.updated_at
            """,
            (settings.discord_webhook_url.strip(), timestamp),
        )
        self.connection.commit()

    def send_creation_notice(self, reminder: Reminder):
        return self._post_payload(self._build_payload("Reminder Created", reminder))

    def send_due_reminder(self, reminder: Reminder):
        return self._post_payload(self._build_payload("Reminder Due", reminder))

    def send_test_message(self):
        return self._post_payload({"content": "Discord webhook test message from BrainForge."})

    def uses_environment_webhook(self) -> bool:
        return bool(os.getenv("DISCORD_WEBHOOK_URL", "").strip())

    def _post_payload(self, payload: dict):
        import requests

        webhook_url = self.get_settings().discord_webhook_url.strip()
        if not webhook_url:
            raise ValueError("Missing Discord webhook URL.")

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=self.timeout_seconds,
            )
        except Exception:
            logger.exception("Discord webhook request raised an unexpected error.")
            raise

        logger.info("Discord webhook response status_code=%s", response.status_code)
        if response.status_code >= 400:
            detail = response.text.strip() or f"HTTP {response.status_code}"
            logger.error(
                "Discord webhook request failed status_code=%s error=%s",
                response.status_code,
                detail[:300],
            )
            raise ValueError(f"Discord webhook request failed: {detail[:300]}")
        return response

    def _build_payload(self, title: str, reminder: Reminder) -> dict:
        reminder_date, reminder_time = self._split_due_at(reminder.due_at)
        category = reminder.category or "Uncategorized"
        note = reminder.description or "-"
        return {
            "embeds": [
                {
                    "title": title,
                    "color": 3447003,
                    "fields": [
                        {"name": "Title", "value": reminder.title or "-", "inline": False},
                        {"name": "Time", "value": f"{reminder_date} {reminder_time}", "inline": False},
                        {"name": "Category", "value": category, "inline": True},
                        {"name": "Note", "value": note, "inline": False},
                    ],
                }
            ]
        }

    def _split_due_at(self, due_at: str) -> tuple[str, str]:
        if not due_at:
            return "-", "-"
        parts = due_at.split(" ", 1)
        if len(parts) == 1:
            return parts[0], "-"
        return parts[0], parts[1]
