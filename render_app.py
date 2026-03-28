from __future__ import annotations

import atexit
import logging
import os
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from waitress import serve

from database.connection import DatabaseManager, open_database_connection
from services.discord_service import DiscordService
from services.reminder_service import ReminderService

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

TAIPEI_TIMEZONE = ZoneInfo("Asia/Taipei")
UTC_TIMEZONE = timezone.utc
POLL_INTERVAL_SECONDS = int(os.getenv("REMINDER_POLL_INTERVAL_SECONDS", "10"))

# DB 固定存 UTC
STORAGE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S+00:00"

# API 固定回台灣時間
API_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

app = Flask(__name__)

database_manager = DatabaseManager()
database_manager.initialize()
scheduler = BackgroundScheduler(timezone=TAIPEI_TIMEZONE)


def _parse_client_datetime(value: str) -> datetime | None:
    """
    前端傳進來的時間：
    - 若無時區，視為 Asia/Taipei
    - 若有時區，轉成 Asia/Taipei
    """
    if not value:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("T", " ")

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=TAIPEI_TIMEZONE)

    return parsed.astimezone(TAIPEI_TIMEZONE)


def _parse_storage_datetime(value: str) -> datetime | None:
    """
    DB 內部時間解析：
    - 若帶 +00:00，當 UTC
    - 若是 naive string，保守視為 UTC
    """
    if not value:
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("T", " ")

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC_TIMEZONE)

    return parsed.astimezone(UTC_TIMEZONE)


def _format_storage_datetime(value: datetime) -> str:
    return value.astimezone(UTC_TIMEZONE).strftime(STORAGE_DATETIME_FORMAT)


def _format_api_datetime(value: datetime) -> str:
    return value.astimezone(TAIPEI_TIMEZONE).strftime(API_DATETIME_FORMAT)


def _convert_storage_text_to_taipei(value: str) -> str:
    """
    把 DB 裡的 UTC 字串安全轉成台灣時間字串
    """
    if not value:
        return ""

    try:
        text = str(value).strip().replace("T", " ")
        parsed = datetime.fromisoformat(text)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC_TIMEZONE)
        else:
            parsed = parsed.astimezone(UTC_TIMEZONE)

        return parsed.astimezone(TAIPEI_TIMEZONE).strftime(API_DATETIME_FORMAT)
    except Exception:
        return value


def _serialize_reminder(reminder) -> dict[str, Any]:
    payload = reminder.to_dict()

    # 所有時間欄位都統一轉成台灣時間回傳
    datetime_fields = [
        "created_at",
        "updated_at",
        "due_at",
        "discord_creation_notice_sent_at",
        "discord_due_notice_sent_at",
    ]

    for field in datetime_fields:
        payload[field] = _convert_storage_text_to_taipei(payload.get(field, ""))

    payload["remind_at"] = payload["due_at"]
    payload["sent"] = bool(payload.get("discord_due_notice_sent_at"))
    return payload


def _open_service_connection():
    return open_database_connection(database_manager.database_path)


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    due_at_value = payload.get("due_at", payload.get("remind_at", ""))
    due_at_text = str(due_at_value).strip()
    normalized_due_at = ""

    if due_at_text:
        parsed_due_at = _parse_client_datetime(due_at_text)
        if parsed_due_at is None:
            raise ValueError("due_at has invalid datetime format")

        # 前端輸入視為台灣時間，存入 DB 時轉 UTC
        normalized_due_at = _format_storage_datetime(parsed_due_at)

    normalized = {
        "title": str(payload.get("title", "")).strip(),
        "category": str(payload.get("category", "")).strip(),
        "description": str(payload.get("description", "")).strip(),
        "due_at": normalized_due_at,
        "priority": int(payload.get("priority", 0)),
        "status": str(payload.get("status", "pending")).strip() or "pending",
    }

    if not normalized["title"]:
        raise ValueError("title is required")

    return normalized


def _mark_reminder_sent(connection, reminder_id: int, sent_at: str) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE reminders
        SET
            discord_due_notice_sent_at = ?,
            status = 'sent',
            last_discord_error = '',
            updated_at = ?
        WHERE id = ?
        """,
        (sent_at, sent_at, reminder_id),
    )
    connection.commit()


def check_due_reminders() -> None:
    logger.info("checking reminders...")
    connection = _open_service_connection()

    try:
        reminder_service = ReminderService(connection)
        discord_service = DiscordService(connection)

        now_taipei = datetime.now(TAIPEI_TIMEZONE)
        now_utc = now_taipei.astimezone(UTC_TIMEZONE)
        reminders = reminder_service.get_pending_discord_reminders()

        logger.info(
            "scheduler tick current_utc_time=%s current_taipei_time=%s pending_count=%s",
            now_utc.isoformat(),
            now_taipei.isoformat(),
            len(reminders),
        )

        for reminder in reminders:
            due_at_datetime = _parse_storage_datetime(reminder.due_at)

            should_send = (
                reminder.status == "pending"
                and not reminder.discord_due_notice_sent_at
                and due_at_datetime is not None
                and now_utc >= due_at_datetime
            )

            logger.info(
                "reminder check reminder_id=%s title=%r current_utc_time=%s current_taipei_time=%s due_at_utc=%s due_at_taipei=%s should_send=%s",
                reminder.id,
                reminder.title,
                now_utc.isoformat(),
                now_taipei.isoformat(),
                due_at_datetime.isoformat() if due_at_datetime else reminder.due_at,
                due_at_datetime.astimezone(TAIPEI_TIMEZONE).isoformat() if due_at_datetime else reminder.due_at,
                should_send,
            )

            if due_at_datetime is None:
                message = f"Unable to parse due_at value: {reminder.due_at!r}"
                reminder_service.mark_discord_failed(reminder.id, message)
                logger.error(
                    "reminder check failed reminder_id=%s title=%r error=%s",
                    reminder.id,
                    reminder.title,
                    message,
                )
                continue

            if not should_send:
                continue

            try:
                response = discord_service.send_due_reminder(reminder)
                sent_at = _format_storage_datetime(datetime.now(TAIPEI_TIMEZONE))
                _mark_reminder_sent(connection, reminder.id, sent_at)

                logger.info(
                    "reminder sent reminder_id=%s title=%r due_at_utc=%s due_at_taipei=%s discord_status_code=%s",
                    reminder.id,
                    reminder.title,
                    due_at_datetime.isoformat(),
                    due_at_datetime.astimezone(TAIPEI_TIMEZONE).isoformat(),
                    response.status_code,
                )
            except Exception as exc:  # pragma: no cover
                reminder_service.mark_discord_failed(reminder.id, str(exc))
                logger.exception(
                    "reminder send failed reminder_id=%s title=%r due_at=%s error=%s",
                    reminder.id,
                    reminder.title,
                    reminder.due_at,
                    exc,
                )
    finally:
        connection.close()


def _start_scheduler() -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        check_due_reminders,
        trigger="interval",
        seconds=POLL_INTERVAL_SECONDS,
        id="check_due_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()

    logger.info(
        "scheduler started timezone=%s poll_interval_seconds=%s",
        TAIPEI_TIMEZONE,
        POLL_INTERVAL_SECONDS,
    )


def _stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("scheduler stopped")


_start_scheduler()
atexit.register(_stop_scheduler)


@app.get("/")
def index():
    return jsonify(
        {
            "service": "BrainForge Render API",
            "status": "ok",
            "health": "/health",
            "test_discord": "/test-discord",
            "reminders": "/api/reminders",
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/test-discord", methods=["GET", "POST"])
def test_discord():
    connection = _open_service_connection()
    try:
        discord_service = DiscordService(connection)
        response = discord_service.send_test_message()
        return jsonify(
            {
                "ok": True,
                "message": "Discord test message sent.",
                "status_code": response.status_code,
            }
        )
    except Exception as exc:
        logger.exception("Discord test endpoint failed error=%s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 400
    finally:
        connection.close()


@app.get("/api/reminders")
def list_reminders():
    connection = _open_service_connection()
    try:
        reminder_service = ReminderService(connection)
        keyword = request.args.get("q", "").strip()
        reminders = (
            reminder_service.search_reminders(keyword)
            if keyword
            else reminder_service.list_reminders()
        )
        return jsonify([_serialize_reminder(reminder) for reminder in reminders])
    finally:
        connection.close()


@app.get("/api/reminders/<int:reminder_id>")
def get_reminder(reminder_id: int):
    connection = _open_service_connection()
    try:
        reminder_service = ReminderService(connection)
        reminder = reminder_service.get_reminder_by_id(reminder_id)
        if reminder is None:
            return jsonify({"error": "Reminder not found."}), 404
        return jsonify(_serialize_reminder(reminder))
    finally:
        connection.close()


@app.post("/api/reminders")
def create_reminder():
    payload = request.get_json(silent=True) or {}
    try:
        validated = _validate_payload(payload)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    connection = _open_service_connection()
    try:
        reminder_service = ReminderService(connection)
        reminder = reminder_service.create_reminder(**validated)

        parsed_due_at_utc = _parse_storage_datetime(reminder.due_at) if reminder.due_at else None

        logger.info(
            "reminder created reminder_id=%s title=%r due_at_utc=%s due_at_taipei=%s sent=%s",
            reminder.id,
            reminder.title,
            parsed_due_at_utc.isoformat() if parsed_due_at_utc else "",
            parsed_due_at_utc.astimezone(TAIPEI_TIMEZONE).isoformat() if parsed_due_at_utc else "",
            bool(reminder.discord_due_notice_sent_at),
        )
        return jsonify(_serialize_reminder(reminder)), 201
    finally:
        connection.close()


@app.put("/api/reminders/<int:reminder_id>")
def update_reminder(reminder_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        validated = _validate_payload(payload)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    connection = _open_service_connection()
    try:
        reminder_service = ReminderService(connection)
        reminder = reminder_service.update_reminder(reminder_id=reminder_id, **validated)
        if reminder is None:
            return jsonify({"error": "Reminder not found."}), 404
        return jsonify(_serialize_reminder(reminder))
    finally:
        connection.close()


@app.delete("/api/reminders/<int:reminder_id>")
def delete_reminder(reminder_id: int):
    connection = _open_service_connection()
    try:
        reminder_service = ReminderService(connection)
        deleted = reminder_service.delete_reminder(reminder_id)
        if not deleted:
            return jsonify({"error": "Reminder not found."}), 404
        return jsonify({"ok": True})
    finally:
        connection.close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    logger.info("Starting Render app on port=%s", port)
    serve(app, host="0.0.0.0", port=port)