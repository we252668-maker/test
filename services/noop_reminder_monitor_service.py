from __future__ import annotations


class NoopReminderMonitorService:
    def start(self) -> None:
        return

    def stop(self) -> None:
        return

    def send_creation_notice_async(self, reminder_id: int) -> None:
        _ = reminder_id
        return
