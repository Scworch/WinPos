"""Toolbar component."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout

from gui.components.material import MaterialButton


class ToolbarWidget(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Toolbar")

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.save_button = MaterialButton("Сохранить")
        self.validate_button = MaterialButton("Проверить")

        layout.addStretch(1)
        layout.addWidget(self.save_button)
        layout.addWidget(self.validate_button)

        self.setLayout(layout)
