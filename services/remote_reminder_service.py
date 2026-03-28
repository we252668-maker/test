from __future__ import annotations

import requests

from models.reminder import Reminder
from services.api_client import ApiClient
from utils.config import BASE_URL


REMINDERS_API_URL = f"{BASE_URL}/api/reminders"


class RemoteReminderService:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def list_reminders(self) -> list[Reminder]:
        data = self.api_client.get(REMINDERS_API_URL).json()
        return [self._map_item(item) for item in data]

    def search_reminders(self, keyword: str) -> list[Reminder]:
        data = self.api_client.get(REMINDERS_API_URL, params={"q": keyword}).json()
        return [self._map_item(item) for item in data]

    def get_reminder_by_id(self, reminder_id: int) -> Reminder | None:
        try:
            response = self.api_client.get(f"{REMINDERS_API_URL}/{reminder_id}")
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise
        return self._map_item(response.json())

    def create_reminder(
        self,
        title: str,
        category: str,
        description: str,
        due_at: str,
        priority: int,
        status: str,
    ) -> Reminder:
        data = self.api_client.post(
            REMINDERS_API_URL,
            json={
                "title": title,
                "category": category,
                "description": description,
                "due_at": due_at,
                "priority": priority,
                "status": status,
            },
        ).json()
        return self._map_item(data)

    def update_reminder(
        self,
        reminder_id: int,
        title: str,
        category: str,
        description: str,
        due_at: str,
        priority: int,
        status: str,
    ) -> Reminder | None:
        try:
            response = self.api_client.put(
                f"{REMINDERS_API_URL}/{reminder_id}",
                json={
                    "title": title,
                    "category": category,
                    "description": description,
                    "due_at": due_at,
                    "priority": priority,
                    "status": status,
                },
            )
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise
        return self._map_item(response.json())

    def delete_reminder(self, reminder_id: int) -> bool:
        try:
            self.api_client.delete(f"{REMINDERS_API_URL}/{reminder_id}")
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return False
            raise
        return True

    def _map_item(self, item: dict) -> Reminder:
        return Reminder(
            id=item.get("id"),
            title=item.get("title", ""),
            category=item.get("category", ""),
            description=item.get("description", ""),
            due_at=item.get("due_at", ""),
            priority=item.get("priority", 0),
            status=item.get("status", "pending"),
            discord_creation_notice_sent_at=item.get("discord_creation_notice_sent_at", ""),
            discord_due_notice_sent_at=item.get("discord_due_notice_sent_at", ""),
            last_discord_error=item.get("last_discord_error", ""),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
        )
