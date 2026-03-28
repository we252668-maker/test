from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox

from views.settings_dialog import SettingsDialog


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
                self.discord_service.send_test_message()
            except Exception:
                QMessageBox.critical(
                    dialog,
                    "Discord Test",
                    "Cloud Discord test failed. Please verify DISCORD_WEBHOOK_URL.",
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
            self.discord_service.send_test_message()
        except Exception:
            QMessageBox.critical(
                dialog,
                "Discord Test",
                "Discord test failed. Please verify the webhook URL.",
            )
            return
        QMessageBox.information(dialog, "Discord Test", "Discord test succeeded.")

    def _uses_environment_webhook(self) -> bool:
        return bool(getattr(self.discord_service, "uses_environment_webhook", lambda: False)())
