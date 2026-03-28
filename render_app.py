from __future__ import annotations

import atexit
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from waitress import serve

from database.connection import DatabaseManager, open_database_connection
from services.discord_service import DiscordService
from services.reminder_monitor_service import ReminderMonitorService
from services.reminder_service import ReminderService

load_dotenv()

app = Flask(__name__)

database_manager = DatabaseManager()
database_manager.initialize()
reminder_monitor_service = ReminderMonitorService(
    database_manager.database_path,
    poll_interval_seconds=int(os.getenv("REMINDER_POLL_INTERVAL_SECONDS", "30")),
)
reminder_monitor_service.start()
atexit.register(reminder_monitor_service.stop)


def _serialize_reminder(reminder) -> dict[str, Any]:
    return reminder.to_dict()


def _open_service_connection():
    return open_database_connection(database_manager.database_path)


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "title": str(payload.get("title", "")).strip(),
        "category": str(payload.get("category", "")).strip(),
        "description": str(payload.get("description", "")).strip(),
        "due_at": str(payload.get("due_at", "")).strip(),
        "priority": int(payload.get("priority", 0)),
        "status": str(payload.get("status", "pending")).strip() or "pending",
    }
    if not normalized["title"]:
        raise ValueError("title is required")
    return normalized


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
        discord_service.send_test_message()
        return jsonify({"ok": True, "message": "Discord test message sent."})
    except Exception as exc:
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
    finally:
        connection.close()

    reminder_monitor_service.send_creation_notice_async(reminder.id)
    return jsonify(_serialize_reminder(reminder)), 201


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
    serve(app, host="0.0.0.0", port=port)
