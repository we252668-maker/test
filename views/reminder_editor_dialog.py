from __future__ import annotations

from PyQt6.QtCore import QDate, QTime
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
)

from models.reminder import Reminder


class ReminderEditorDialog(QDialog):
    def __init__(self, parent=None, reminder: Reminder | None = None) -> None:
        super().__init__(parent)
        self.reminder = reminder
        self.setWindowTitle("編輯提醒" if reminder else "新增提醒")
        self.resize(520, 460)

        self.title_input = QLineEdit()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("例如：工作、會議、繳費")
        self.description_input = QTextEdit()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTime(QTime.currentTime())

        self.priority_input = QSpinBox()
        self.priority_input.setRange(0, 5)

        self.status_input = QComboBox()
        self.status_input.addItems(["pending", "done", "cancelled"])

        form_layout = QFormLayout()
        form_layout.addRow("標題", self.title_input)
        form_layout.addRow("分類", self.category_input)
        form_layout.addRow("日期", self.date_input)
        form_layout.addRow("時間", self.time_input)
        form_layout.addRow("優先度", self.priority_input)
        form_layout.addRow("狀態", self.status_input)
        form_layout.addRow("備註", self.description_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        if reminder is not None:
            self._populate(reminder)

    def _populate(self, reminder: Reminder) -> None:
        self.title_input.setText(reminder.title)
        self.category_input.setText(reminder.category)
        self.description_input.setPlainText(reminder.description)
        if reminder.due_at:
            date_part, time_part = self._split_due_at(reminder.due_at)
            parsed_date = QDate.fromString(date_part, "yyyy-MM-dd")
            parsed_time = QTime.fromString(time_part, "HH:mm:ss")
            if parsed_date.isValid():
                self.date_input.setDate(parsed_date)
            if parsed_time.isValid():
                self.time_input.setTime(parsed_time)
        self.priority_input.setValue(reminder.priority)
        index = self.status_input.findText(reminder.status)
        if index >= 0:
            self.status_input.setCurrentIndex(index)

    def get_payload(self) -> dict:
        due_at = f"{self.date_input.date().toString('yyyy-MM-dd')} {self.time_input.time().toString('HH:mm:ss')}"
        return {
            "title": self.title_input.text().strip(),
            "category": self.category_input.text().strip() or "未分類",
            "description": self.description_input.toPlainText().strip(),
            "due_at": due_at,
            "priority": self.priority_input.value(),
            "status": self.status_input.currentText(),
        }

    def _validate_and_accept(self) -> None:
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "欄位未填", "請輸入提醒標題。")
            self.title_input.setFocus()
            return
        self.accept()

    def _split_due_at(self, due_at: str) -> tuple[str, str]:
        parts = due_at.split(" ", 1)
        if len(parts) == 1:
            return parts[0], "00:00:00"
        return parts[0], parts[1]
