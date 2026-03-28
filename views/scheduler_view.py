from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.reminder import Reminder


class SchedulerView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.page_title = QLabel("提醒管理")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: 600;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋標題、日期、分類或備註")
        self.search_button = QPushButton("搜尋")
        self.reset_button = QPushButton("重設")

        self.create_button = QPushButton("新增提醒")
        self.edit_button = QPushButton("編輯提醒")
        self.delete_button = QPushButton("刪除提醒")

        self.reminder_list = QListWidget()
        self.reminder_list.setMinimumWidth(320)
        self.result_label = QLabel("共 0 筆提醒")

        self.detail_title_label = QLabel("請先選擇提醒")
        self.detail_title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.detail_title_label.setWordWrap(True)
        self.detail_meta_label = QLabel(
            "日期：-\n時間：-\n分類：-\n狀態：-\n優先度：-\nDiscord 通知：-"
        )
        self.detail_meta_label.setWordWrap(True)
        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        self.detail_description.setPlaceholderText("提醒備註會顯示在這裡")

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_button)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.create_button)
        action_layout.addWidget(self.edit_button)
        action_layout.addWidget(self.delete_button)
        action_layout.addStretch()

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.result_label)
        left_layout.addWidget(self.reminder_list)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.detail_title_label)
        right_layout.addWidget(self.detail_meta_label)
        right_layout.addWidget(self.detail_description)
        right_panel.setLayout(right_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 5)

        layout = QVBoxLayout()
        layout.addWidget(self.page_title)
        layout.addLayout(search_layout)
        layout.addLayout(action_layout)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def populate_reminders(self, reminders: list[Reminder]) -> None:
        self.reminder_list.clear()
        for reminder in reminders:
            due_at = reminder.due_at or "未排程"
            item = QListWidgetItem(f"{reminder.title} | {reminder.category} | {due_at}")
            item.setData(Qt.ItemDataRole.UserRole, reminder.id)
            self.reminder_list.addItem(item)
        self.result_label.setText(f"共 {len(reminders)} 筆提醒")

    def current_reminder_id(self) -> int | None:
        item = self.reminder_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def select_reminder_by_id(self, reminder_id: int) -> None:
        for index in range(self.reminder_list.count()):
            item = self.reminder_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == reminder_id:
                self.reminder_list.setCurrentItem(item)
                return

    def show_reminder_details(self, reminder: Reminder | None) -> None:
        if reminder is None:
            self.detail_title_label.setText("請先選擇提醒")
            self.detail_meta_label.setText("日期：-\n時間：-\n分類：-\n狀態：-\n優先度：-\nDiscord 通知：-")
            self.detail_description.clear()
            return

        date_text, time_text = self._split_due_at(reminder.due_at)
        discord_status = "待發送建立通知"
        if reminder.discord_creation_notice_sent_at:
            discord_status = f"建立通知已發送 ({reminder.discord_creation_notice_sent_at})"
        if reminder.discord_due_notice_sent_at:
            discord_status = f"到期通知已發送 ({reminder.discord_due_notice_sent_at})"
        elif reminder.last_discord_error:
            discord_status = f"失敗: {reminder.last_discord_error}"

        self.detail_title_label.setText(reminder.title)
        self.detail_meta_label.setText(
            f"日期：{date_text}\n"
            f"時間：{time_text}\n"
            f"分類：{reminder.category or '未分類'}\n"
            f"狀態：{self._translate_status(reminder.status)}\n"
            f"優先度：{reminder.priority}\n"
            f"Discord 通知：{discord_status}"
        )
        self.detail_description.setPlainText(reminder.description)

    def _split_due_at(self, due_at: str) -> tuple[str, str]:
        if not due_at:
            return "-", "-"
        parts = due_at.split(" ", 1)
        if len(parts) == 1:
            return parts[0], "-"
        return parts[0], parts[1]

    def _translate_status(self, status: str) -> str:
        mapping = {
            "pending": "待處理",
            "done": "已完成",
            "cancelled": "已取消",
        }
        return mapping.get(status, status)
