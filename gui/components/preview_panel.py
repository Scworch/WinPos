"""Preview panel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout

from gui.components.material import MaterialCard


class PreviewPanel(MaterialCard):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Предпросмотр")
        title.setObjectName("PanelTitle")

        self.preview_box = QPlainTextEdit()
        self.preview_box.setReadOnly(True)

        layout = self.body
        layout.addWidget(title)
        layout.addWidget(self.preview_box)
