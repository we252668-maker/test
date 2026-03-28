from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from models.settings_model import SettingsModel


class SettingsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("通知設定")
        self.resize(520, 220)

        self.discord_webhook_input = QLineEdit()
        self.discord_webhook_input.setPlaceholderText("請輸入 Discord Webhook URL")

        self.discord_connect_button = QPushButton("連接 Discord")

        discord_form_layout = QFormLayout()
        discord_form_layout.addRow("Discord Webhook URL", self.discord_webhook_input)

        discord_group = QGroupBox("Discord 通知設定")
        discord_group.setLayout(discord_form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )

        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.discord_connect_button)
        footer_layout.addStretch()
        footer_layout.addWidget(self.button_box)

        root_layout = QVBoxLayout()
        root_layout.addWidget(discord_group)
        root_layout.addLayout(footer_layout)
        self.setLayout(root_layout)

    def set_settings(self, settings: SettingsModel) -> None:
        self.discord_webhook_input.setText(settings.discord_webhook_url)

    def get_settings(self) -> SettingsModel:
        return SettingsModel(discord_webhook_url=self.discord_webhook_input.text().strip())
