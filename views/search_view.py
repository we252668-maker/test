from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models.search_result import SearchResult


class SearchView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.page_title = QLabel("全域搜尋")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: 600;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("請輸入搜尋關鍵字，可搜尋提醒、筆記與程式碼片段")
        self.search_button = QPushButton("搜尋")
        self.reset_button = QPushButton("清除")
        self.open_button = QPushButton("前往來源")

        self.result_label = QLabel("目前共有 0 筆結果")
        self.results_list = QListWidget()

        self.detail_title_label = QLabel("請先輸入搜尋關鍵字")
        self.detail_title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.detail_meta_label = QLabel("來源：-\n說明：-")
        self.detail_meta_label.setWordWrap(True)
        self.detail_preview = QTextEdit()
        self.detail_preview.setReadOnly(True)
        self.detail_preview.setPlaceholderText("搜尋結果預覽會顯示在這裡")

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.search_button)
        toolbar_layout.addWidget(self.reset_button)
        toolbar_layout.addWidget(self.open_button)

        layout = QVBoxLayout()
        layout.addWidget(self.page_title)
        layout.addLayout(toolbar_layout)
        layout.addWidget(self.result_label)
        layout.addWidget(self.results_list)
        layout.addWidget(self.detail_title_label)
        layout.addWidget(self.detail_meta_label)
        layout.addWidget(self.detail_preview)
        self.setLayout(layout)

    def populate_results(self, results: list[SearchResult]) -> None:
        self.results_list.clear()
        for result in results:
            item = QListWidgetItem(result.display_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
        self.result_label.setText(f"目前共有 {len(results)} 筆結果")

    def current_result(self) -> SearchResult | None:
        item = self.results_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def show_result_details(self, result: SearchResult | None) -> None:
        if result is None:
            self.detail_title_label.setText("請先輸入搜尋關鍵字")
            self.detail_meta_label.setText("來源：-\n說明：-")
            self.detail_preview.clear()
            return

        self.detail_title_label.setText(result.title)
        tags_text = f"\n標籤：{result.tags_text}" if result.tags_text else ""
        self.detail_meta_label.setText(f"來源：{result.source_type}\n說明：{result.subtitle}{tags_text}")
        self.detail_preview.setPlainText(result.content_preview)
