"""Profiles panel."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout

from gui.components.material import MaterialButton, MaterialCard


class ProfilesPanel(MaterialCard):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Профили")
        title.setObjectName("PanelTitle")

        self.profile_combo = QComboBox()
        self.add_profile_btn = MaterialButton("Добавить")
        self.edit_profile_btn = MaterialButton("Редактировать")

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(self.add_profile_btn)
        button_row.addWidget(self.edit_profile_btn)

        layout = self.body
        layout.addWidget(title)
        layout.addWidget(self.profile_combo)
        layout.addLayout(button_row)
