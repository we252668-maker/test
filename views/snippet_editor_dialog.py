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

from models.code_snippet import CodeSnippet


class SnippetEditorDialog(QDialog):
    def __init__(self, parent=None, snippet: CodeSnippet | None = None) -> None:
        super().__init__(parent)
        self.snippet = snippet
        self.setWindowTitle("編輯程式碼片段" if snippet else "新增程式碼片段")
        self.resize(760, 620)

        self.title_input = QLineEdit()
        self.language_input = QLineEdit()
        self.tags_input = QLineEdit()
        self.description_input = QTextEdit()
        self.code_input = QTextEdit()

        self.title_input.setPlaceholderText("例如：SQLite 連線工具")
        self.language_input.setPlaceholderText("例如：python")
        self.tags_input.setPlaceholderText("請輸入標籤，使用逗號分隔，例如：db, util, pyqt")
        self.description_input.setPlaceholderText("請輸入這段程式碼的用途說明")
        self.code_input.setPlaceholderText("請貼上程式碼內容")

        form_layout = QFormLayout()
        form_layout.addRow("標題", self.title_input)
        form_layout.addRow("語言", self.language_input)
        form_layout.addRow("標籤", self.tags_input)
        form_layout.addRow("說明", self.description_input)
        form_layout.addRow("程式碼", self.code_input)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        if snippet is not None:
            self._populate(snippet)

    def _populate(self, snippet: CodeSnippet) -> None:
        self.title_input.setText(snippet.title)
        self.language_input.setText(snippet.language)
        self.tags_input.setText(snippet.tag_text)
        self.description_input.setPlainText(snippet.description)
        self.code_input.setPlainText(snippet.code)

    def get_payload(self) -> dict:
        return {
            "title": self.title_input.text().strip(),
            "language": self.language_input.text().strip() or "text",
            "description": self.description_input.toPlainText().strip(),
            "code": self.code_input.toPlainText(),
            "tags": [tag.strip() for tag in self.tags_input.text().split(",") if tag.strip()],
        }

    def _validate_and_accept(self) -> None:
        payload = self.get_payload()
        if not payload["title"]:
            QMessageBox.warning(self, "資料不完整", "請輸入程式碼片段標題。")
            self.title_input.setFocus()
            return
        if not payload["code"].strip():
            QMessageBox.warning(self, "資料不完整", "請輸入程式碼內容。")
            self.code_input.setFocus()
            return
        self.accept()
