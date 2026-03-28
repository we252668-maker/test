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

from models.note import Note


class NoteView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.page_title = QLabel("研發心得 / 技術筆記")
        self.page_title.setStyleSheet("font-size: 20px; font-weight: 600;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("請輸入標題、內容或標籤")
        self.search_button = QPushButton("搜尋")
        self.reset_button = QPushButton("清除")

        self.create_button = QPushButton("新增筆記")
        self.edit_button = QPushButton("編輯筆記")
        self.delete_button = QPushButton("刪除筆記")

        self.note_list = QListWidget()
        self.note_list.setMinimumWidth(320)

        self.detail_title_label = QLabel("請先從左側選擇一篇筆記")
        self.detail_title_label.setWordWrap(True)
        self.detail_title_label.setStyleSheet("font-size: 18px; font-weight: 600;")

        self.detail_meta_label = QLabel("標籤：-\n最後更新：-")
        self.detail_meta_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_meta_label.setWordWrap(True)
        self.attachment_placeholder_label = QLabel("附件區：保留給未來附件管理與檔案預覽")

        self.detail_content = QTextEdit()
        self.detail_content.setReadOnly(True)
        self.detail_content.setPlaceholderText("筆記內容會顯示在這裡")

        self.result_label = QLabel("目前共有 0 篇筆記")

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
        left_layout.addWidget(self.note_list)
        left_panel.setLayout(left_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.detail_title_label)
        right_layout.addWidget(self.detail_meta_label)
        right_layout.addWidget(self.attachment_placeholder_label)
        right_layout.addWidget(self.detail_content)
        right_panel.setLayout(right_layout)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 5)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.page_title)
        root_layout.addLayout(search_layout)
        root_layout.addLayout(action_layout)
        root_layout.addWidget(content_splitter)
        self.setLayout(root_layout)

    def populate_notes(self, notes: list[Note]) -> None:
        self.note_list.clear()

        for note in notes:
            display_text = note.title
            if note.tag_text:
                display_text = f"{display_text} | {note.tag_text}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            self.note_list.addItem(item)

        self.result_label.setText(f"目前共有 {len(notes)} 篇筆記")

    def current_note_id(self) -> int | None:
        item = self.note_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def select_note_by_id(self, note_id: int) -> None:
        for index in range(self.note_list.count()):
            item = self.note_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.note_list.setCurrentItem(item)
                return

    def show_note_details(self, note: Note | None) -> None:
        if note is None:
            self.detail_title_label.setText("請先從左側選擇一篇筆記")
            self.detail_meta_label.setText("標籤：-\n最後更新：-")
            self.detail_content.clear()
            return

        tags_text = note.tag_text if note.tag_text else "-"
        updated_at = note.updated_at or note.created_at or "-"
        self.detail_title_label.setText(note.title)
        self.detail_meta_label.setText(f"標籤：{tags_text}\n最後更新：{updated_at}")
        self.detail_content.setPlainText(note.content)
