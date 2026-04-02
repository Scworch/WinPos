"""Applications panel."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QVBoxLayout

from gui.components.material import MaterialButton, MaterialCard


class ApplicationsPanel(MaterialCard):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Приложения")
        title.setObjectName("PanelTitle")

        self.app_list = QListWidget()
        self.add_app_btn = MaterialButton("Добавить")
        self.edit_app_btn = MaterialButton("Изменить")
        self.remove_app_btn = MaterialButton("Удалить")

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.add_app_btn)
        button_row.addWidget(self.edit_app_btn)
        button_row.addWidget(self.remove_app_btn)

        layout = self.body
        layout.addWidget(title)
        layout.addWidget(self.app_list)
        layout.addLayout(button_row)
