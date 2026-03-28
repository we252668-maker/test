from __future__ import annotations

import logging
import sqlite3
import threading
from pathlib import Path

from services.discord_service import DiscordService
from services.reminder_service import ReminderService


logger = logging.getLogger(__name__)


class ReminderMonitorService:
    def __init__(self, database_path: Path, poll_interval_seconds: int = 30) -> None:
        self.database_path = Path(database_path)
        self.poll_interval_seconds = poll_interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            logger.info("Reminder scheduler already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            name="reminder-monitor",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "Reminder scheduler started. poll_interval_seconds=%s database_path=%s",
            self.poll_interval_seconds,
            self.database_path,
        )

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        logger.info("Reminder scheduler stopped.")

    def send_creation_notice_async(self, reminder_id: int) -> None:
        _ = reminder_id
        logger.info(
            "Creation notice dispatch skipped for Render API. reminder_id=%s",
            reminder_id,
        )

    def _monitor_loop(self) -> None:
        logger.info("Reminder monitor loop is running.")
        while not self._stop_event.is_set():
            try:
                self._process_due_reminders()
            except Exception:
                logger.exception("Reminder monitor loop crashed while processing reminders.")
            self._stop_event.wait(self.poll_interval_seconds)

    def _process_due_reminders(self) -> None:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            reminder_service = ReminderService(connection)
            discord_service = DiscordService(connection)
            current_time = reminder_service.current_time()
            reminders = reminder_service.get_pending_discord_reminders()

            logger.info(
                "Reminder scheduler tick. current_time=%s pending_count=%s",
                reminder_service.format_datetime(current_time),
                len(reminders),
            )

            for reminder in reminders:
                remind_at = reminder_service.parse_due_at(reminder.due_at)
                should_send = remind_at is not None and current_time >= remind_at
                logger.info(
                    "Reminder check id=%s title=%r remind_at=%s current_time=%s should_send=%s sent=%s",
                    reminder.id,
                    reminder.title,
                    reminder_service.format_datetime(remind_at),
                    reminder_service.format_datetime(current_time),
                    should_send,
                    bool(reminder.discord_due_notice_sent_at),
                )

                if remind_at is None:
                    message = f"Unable to parse due_at/remind_at value: {reminder.due_at!r}"
                    logger.error(
                        "Reminder check failed id=%s title=%r error=%s",
                        reminder.id,
                        reminder.title,
                        message,
                    )
                    reminder_service.mark_discord_failed(reminder.id, message)
                    continue

                if not should_send:
                    continue

                try:
                    response = discord_service.send_due_reminder(reminder)
                    reminder_service.mark_discord_due_notice_sent(reminder.id)
                    logger.info(
                        "Reminder sent successfully id=%s title=%r remind_at=%s current_time=%s should_send=%s discord_status_code=%s",
                        reminder.id,
                        reminder.title,
                        reminder_service.format_datetime(remind_at),
                        reminder_service.format_datetime(current_time),
                        should_send,
                        response.status_code,
                    )
                except Exception as exc:  # pragma: no cover
                    reminder_service.mark_discord_failed(reminder.id, str(exc))
                    logger.exception(
                        "Reminder send failed id=%s title=%r remind_at=%s current_time=%s should_send=%s error=%s",
                        reminder.id,
                        reminder.title,
                        reminder_service.format_datetime(remind_at),
                        reminder_service.format_datetime(current_time),
                        should_send,
                        exc,
                    )
        finally:
            connection.close()
