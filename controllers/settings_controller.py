from __future__ import annotations

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

from views.settings_dialog import SettingsDialog


TIMEOUT_MESSAGE = "\u96f2\u7aef\u670d\u52d9\u559a\u9192\u4e2d\uff0c\u8acb\u518d\u8a66\u4e00\u6b21"
LOADING_TEXT = "\u8f09\u5165\u4e2d..."


class SettingsController:
    def __init__(self, discord_service, parent=None) -> None:
        self.discord_service = discord_service
        self.parent = parent

    def open_notification_settings(self) -> None:
        dialog = SettingsDialog(self.parent)
        dialog.set_settings(self.discord_service.get_settings())

        if self._uses_environment_webhook():
            dialog.discord_webhook_input.setReadOnly(True)
            dialog.discord_webhook_input.setPlaceholderText(
                "Managed by DISCORD_WEBHOOK_URL in cloud environment."
            )

        dialog.button_box.accepted.connect(lambda: self._save_settings(dialog))
        dialog.button_box.rejected.connect(dialog.reject)
        dialog.discord_connect_button.clicked.connect(lambda: self._connect_discord(dialog))
        dialog.exec()

    def _save_settings(self, dialog: SettingsDialog) -> None:
        if self._uses_environment_webhook():
            QMessageBox.information(
                dialog,
                "Cloud Managed",
                "Discord webhook is managed by DISCORD_WEBHOOK_URL and does not need local saving.",
            )
            dialog.accept()
            return

        settings = dialog.get_settings()
        self.discord_service.save_settings(settings)
        QMessageBox.information(dialog, "Saved", "Discord webhook settings saved.")
        dialog.accept()

    def _connect_discord(self, dialog: SettingsDialog) -> None:
        if self._uses_environment_webhook():
            try:
                self._run_with_loading(dialog, self.discord_service.send_test_message)
            except Exception as exc:
                QMessageBox.critical(
                    dialog,
                    "Discord Test",
                    self._format_api_error(
                        "Cloud Discord test failed. Please verify DISCORD_WEBHOOK_URL.",
                        exc,
                    ),
                )
                return
            QMessageBox.information(dialog, "Discord Test", "Cloud Discord test succeeded.")
            return

        settings = dialog.get_settings()
        if not settings.discord_webhook_url:
            QMessageBox.warning(dialog, "Discord Test", "Please enter a Discord webhook URL.")
            return

        self.discord_service.save_settings(settings)
        try:
            self._run_with_loading(dialog, self.discord_service.send_test_message)
        except Exception as exc:
            QMessageBox.critical(
                dialog,
                "Discord Test",
                self._format_api_error("Discord test failed. Please verify the webhook URL.", exc),
            )
            return
        QMessageBox.information(dialog, "Discord Test", "Discord test succeeded.")

    def _uses_environment_webhook(self) -> bool:
        return bool(getattr(self.discord_service, "uses_environment_webhook", lambda: False)())

    def _format_api_error(self, message: str, exc: Exception) -> str:
        if isinstance(exc, requests.Timeout):
            detail = TIMEOUT_MESSAGE
            return f"{message}\n\n{detail}"
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                detail = response.text.strip()
            except Exception:
                detail = str(exc)
        elif isinstance(exc, requests.RequestException):
            detail = str(exc)
        else:
            detail = str(exc)
        return message if not detail else f"{message}\n\n{detail}"

    def _run_with_loading(self, dialog: SettingsDialog, operation):
        self._set_loading_state(dialog, True)
        try:
            return operation()
        finally:
            self._set_loading_state(dialog, False)

    def _set_loading_state(self, dialog: SettingsDialog, is_loading: bool) -> None:
        dialog.setCursor(Qt.CursorShape.WaitCursor if is_loading else Qt.CursorShape.ArrowCursor)
        dialog.discord_connect_button.setDisabled(is_loading)
        dialog.button_box.setDisabled(is_loading)
        dialog.setToolTip(LOADING_TEXT if is_loading else "")
        dialog.repaint()
        QApplication.processEvents()
