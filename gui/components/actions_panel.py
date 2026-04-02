"""Actions panel."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QVBoxLayout

from gui.components.material import MaterialButton, MaterialCard


class ActionsPanel(MaterialCard):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Действия")
        title.setObjectName("PanelTitle")

        self.action_list = QListWidget()
        self.add_action_btn = MaterialButton("Добавить")
        self.edit_action_btn = MaterialButton("Изменить")
        self.remove_action_btn = MaterialButton("Удалить")
        self.up_btn = MaterialButton("Вверх")
        self.down_btn = MaterialButton("Вниз")

        row_top = QHBoxLayout()
        row_top.setSpacing(8)
        row_top.addWidget(self.add_action_btn)
        row_top.addWidget(self.edit_action_btn)
        row_top.addWidget(self.remove_action_btn)

        row_bottom = QHBoxLayout()
        row_bottom.setSpacing(8)
        row_bottom.addWidget(self.up_btn)
        row_bottom.addWidget(self.down_btn)

        layout = self.body
        layout.addWidget(title)
        layout.addWidget(self.action_list)
        layout.addLayout(row_top)
        layout.addLayout(row_bottom)
