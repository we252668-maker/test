from __future__ import annotations

import sqlite3
from datetime import datetime

from models.reminder import Reminder
from models.settings_model import SettingsModel


class DiscordService:
    def __init__(self, connection: sqlite3.Connection, timeout_seconds: int = 10) -> None:
        self.connection = connection
        self.timeout_seconds = timeout_seconds

    def get_settings(self) -> SettingsModel:
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

    def send_creation_notice(self, reminder: Reminder) -> None:
        self._post_payload(self._build_payload("提醒建立成功", reminder))

    def send_due_reminder(self, reminder: Reminder) -> None:
        self._post_payload(self._build_payload("提醒時間已到", reminder))

    def send_test_message(self) -> None:
        self._post_payload({"content": "Discord 連接測試成功"})

    def _post_payload(self, payload: dict) -> None:
        import requests

        settings = self.get_settings()
        webhook_url = settings.discord_webhook_url.strip()
        if not webhook_url:
            raise ValueError("請先輸入 Discord Webhook URL")

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=self.timeout_seconds,
        )
        if response.status_code >= 400:
            detail = response.text.strip() or f"HTTP {response.status_code}"
            raise ValueError(f"Discord 通知發送失敗：{detail[:300]}")

    def _build_payload(self, title: str, reminder: Reminder) -> dict:
        reminder_date, reminder_time = self._split_due_at(reminder.due_at)
        category = reminder.category or "未分類"
        note = reminder.description or "-"
        return {
            "embeds": [
                {
                    "title": title,
                    "color": 3447003,
                    "fields": [
                        {"name": "標題", "value": reminder.title or "-", "inline": False},
                        {"name": "時間", "value": f"{reminder_date} {reminder_time}", "inline": False},
                        {"name": "分類", "value": category, "inline": True},
                        {"name": "備註", "value": note, "inline": False},
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
