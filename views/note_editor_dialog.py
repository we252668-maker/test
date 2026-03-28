from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from models.note import Note


class NoteEditorDialog(QDialog):
    def __init__(self, parent=None, note: Note | None = None) -> None:
        super().__init__(parent)
        self.note = note
        self.setWindowTitle("編輯技術筆記" if note else "新增技術筆記")
        self.resize(640, 520)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("請輸入筆記標題")

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("請輸入標籤，使用逗號分隔，例如：PyQt, SQLite, 架構")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("請輸入技術筆記內容")

        form_layout = QFormLayout()
        form_layout.addRow("標題", self.title_input)
        form_layout.addRow("標籤", self.tags_input)
        form_layout.addRow("內容", self.content_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        if note is not None:
            self._populate(note)

    def _populate(self, note: Note) -> None:
        self.title_input.setText(note.title)
        self.tags_input.setText(note.tag_text)
        self.content_input.setPlainText(note.content)

    def get_payload(self) -> dict:
        return {
            "title": self.title_input.text().strip(),
            "content": self.content_input.toPlainText().strip(),
            "tags": [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()],
        }

    def _validate_and_accept(self) -> None:
        payload = self.get_payload()
        if not payload["title"]:
            QMessageBox.warning(self, "資料不完整", "請輸入筆記標題。")
            self.title_input.setFocus()
            return

        if not payload["content"]:
            QMessageBox.warning(self, "資料不完整", "請輸入筆記內容。")
            self.content_input.setFocus()
            return

        self.accept()
