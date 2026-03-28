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

from models.code_snippet import CodeSnippet


class SnippetView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.page_title = QLabel("程式碼片段")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: 600;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("請輸入標題、語言、描述、程式碼或標籤")
        self.search_button = QPushButton("搜尋")
        self.reset_button = QPushButton("清除")

        self.create_button = QPushButton("新增片段")
        self.edit_button = QPushButton("編輯片段")
        self.delete_button = QPushButton("刪除片段")

        self.snippet_list = QListWidget()
        self.snippet_list.setMinimumWidth(340)
        self.result_label = QLabel("目前共有 0 筆程式碼片段")

        self.detail_title_label = QLabel("請先從左側選擇一段程式碼")
        self.detail_title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.detail_title_label.setWordWrap(True)
        self.detail_meta_label = QLabel("語言：-\n標籤：-\n最後更新：-")
        self.detail_meta_label.setWordWrap(True)
        self.attachment_placeholder_label = QLabel("附件區：保留給未來附件管理與檔案預覽")
        self.preview_placeholder_label = QLabel("程式碼預覽：保留給未來語法高亮與預覽引擎")
        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        self.detail_description.setPlaceholderText("說明會顯示在這裡")
        self.detail_code = QTextEdit()
        self.detail_code.setReadOnly(True)
        self.detail_code.setPlaceholderText("程式碼會顯示在這裡")

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
        left_layout.addWidget(self.snippet_list)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.detail_title_label)
        right_layout.addWidget(self.detail_meta_label)
        right_layout.addWidget(self.attachment_placeholder_label)
        right_layout.addWidget(self.preview_placeholder_label)
        right_layout.addWidget(self.detail_description)
        right_layout.addWidget(self.detail_code)
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

    def populate_snippets(self, snippets: list[CodeSnippet]) -> None:
        self.snippet_list.clear()
        for snippet in snippets:
            item = QListWidgetItem(f"{snippet.title} | {snippet.language}")
            item.setData(Qt.ItemDataRole.UserRole, snippet.id)
            self.snippet_list.addItem(item)
        self.result_label.setText(f"目前共有 {len(snippets)} 筆程式碼片段")

    def current_snippet_id(self) -> int | None:
        item = self.snippet_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def select_snippet_by_id(self, snippet_id: int) -> None:
        for index in range(self.snippet_list.count()):
            item = self.snippet_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == snippet_id:
                self.snippet_list.setCurrentItem(item)
                return

    def show_snippet_details(self, snippet: CodeSnippet | None) -> None:
        if snippet is None:
            self.detail_title_label.setText("請先從左側選擇一段程式碼")
            self.detail_meta_label.setText("語言：-\n標籤：-\n最後更新：-")
            self.detail_description.clear()
            self.detail_code.clear()
            return

        self.detail_title_label.setText(snippet.title)
        self.detail_meta_label.setText(
            f"語言：{snippet.language}\n標籤：{snippet.tag_text or '-'}\n最後更新：{snippet.updated_at or '-'}"
        )
        self.detail_description.setPlainText(snippet.description)
        self.detail_code.setPlainText(snippet.code)
