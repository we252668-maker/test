from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from services.discord_service import DiscordService
from services.reminder_service import ReminderService


class ReminderMonitorService:
    def __init__(self, database_path: Path, poll_interval_seconds: int = 30) -> None:
        self.database_path = Path(database_path)
        self.poll_interval_seconds = poll_interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="reminder-monitor",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def send_creation_notice_async(self, reminder_id: int) -> None:
        worker = threading.Thread(
            target=self._send_creation_notice,
            args=(reminder_id,),
            name=f"creation-notice-{reminder_id}",
            daemon=True,
        )
        worker.start()

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            self._process_due_reminders()
            self._stop_event.wait(self.poll_interval_seconds)

    def _send_creation_notice(self, reminder_id: int) -> None:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            reminder_service = ReminderService(connection)
            discord_service = DiscordService(connection)
            reminder = reminder_service.get_reminder_by_id(reminder_id)
            if reminder is None or reminder.discord_creation_notice_sent_at:
                return

            try:
                discord_service.send_creation_notice(reminder)
                reminder_service.mark_discord_creation_notice_sent(reminder.id)
            except Exception as exc:  # pragma: no cover
                reminder_service.mark_discord_failed(reminder.id, str(exc))
        finally:
            connection.close()

    def _process_due_reminders(self) -> None:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            reminder_service = ReminderService(connection)
            discord_service = DiscordService(connection)

            for reminder in reminder_service.get_due_discord_reminders():
                try:
                    discord_service.send_due_reminder(reminder)
                    reminder_service.mark_discord_due_notice_sent(reminder.id)
                except Exception as exc:  # pragma: no cover
                    reminder_service.mark_discord_failed(reminder.id, str(exc))
        finally:
            connection.close()
