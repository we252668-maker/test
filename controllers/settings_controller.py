from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox

from services.discord_service import DiscordService
from views.settings_dialog import SettingsDialog


class SettingsController:
    def __init__(self, discord_service: DiscordService, parent=None) -> None:
        self.discord_service = discord_service
        self.parent = parent

    def open_notification_settings(self) -> None:
        dialog = SettingsDialog(self.parent)
        dialog.set_settings(self.discord_service.get_settings())
        dialog.button_box.accepted.connect(lambda: self._save_settings(dialog))
        dialog.button_box.rejected.connect(dialog.reject)
        dialog.discord_connect_button.clicked.connect(lambda: self._connect_discord(dialog))
        dialog.exec()

    def _save_settings(self, dialog: SettingsDialog) -> None:
        settings = dialog.get_settings()
        self.discord_service.save_settings(settings)
        QMessageBox.information(dialog, "設定已儲存", "通知設定已更新")
        dialog.accept()

    def _connect_discord(self, dialog: SettingsDialog) -> None:
        settings = dialog.get_settings()
        if not settings.discord_webhook_url:
            QMessageBox.warning(dialog, "Discord 連接失敗", "請先輸入 Discord Webhook URL")
            return

        self.discord_service.save_settings(settings)
        try:
            self.discord_service.send_test_message()
        except Exception:
            QMessageBox.critical(dialog, "Discord 連接失敗", "Discord 連接失敗，請檢查 Webhook URL")
            return
        QMessageBox.information(dialog, "Discord 連接成功", "Discord 連接成功")
