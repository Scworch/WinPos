"""Main GUI window."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSystemTrayIcon,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from gui.config_store import ConfigStore
from gui.dialogs import AppDialog, ActionDialog, ProfileDialog, ACTION_DEFS
from gui.components.toolbar import ToolbarWidget
from gui.components.profiles_panel import ProfilesPanel
from gui.components.applications_panel import ApplicationsPanel
from gui.components.details_card import DetailsCard
from gui.components.actions_panel import ActionsPanel
from gui.components.preview_panel import PreviewPanel
from monitors.monitor_manager import MonitorManager


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WinPos")
        self.resize(1280, 760)

        self.config_path = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
        self.store = ConfigStore(self.config_path)
        self.data: Dict[str, Any] = self.store.load()
        self._is_vertical = False
        self._allow_close = False

        self._setup_ui()
        self._setup_tray()
        self._refresh_profiles()
        self._refresh_apps()

    def _setup_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 16)
        root.setSpacing(12)

        self.toolbar = ToolbarWidget()
        self.toolbar.save_button.clicked.connect(self.save_config)
        self.toolbar.validate_button.clicked.connect(self.validate_config)

        root.addWidget(self.toolbar)

        self.content = QWidget()
        self.content_layout = QBoxLayout(QBoxLayout.LeftToRight)
        self.content_layout.setSpacing(18)
        self.content_layout.setContentsMargins(16, 12, 16, 0)
        self.content.setLayout(self.content_layout)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setSpacing(14)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel.setLayout(self.left_layout)

        self.center_panel = QWidget()
        self.center_layout = QVBoxLayout()
        self.center_layout.setSpacing(14)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_panel.setLayout(self.center_layout)

        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(14)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_panel.setLayout(self.right_layout)

        self.profiles_panel = ProfilesPanel()
        self.profiles_panel.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        self.profiles_panel.add_profile_btn.clicked.connect(self.add_profile)
        self.profiles_panel.edit_profile_btn.clicked.connect(self.edit_profile)

        self.apps_panel = ApplicationsPanel()
        self.apps_panel.app_list.currentItemChanged.connect(self._on_app_selected)
        self.apps_panel.add_app_btn.clicked.connect(self.add_app)
        self.apps_panel.edit_app_btn.clicked.connect(self.edit_app)
        self.apps_panel.remove_app_btn.clicked.connect(self.remove_app)

        self.details_card = DetailsCard()
        self.actions_panel = ActionsPanel()
        self.actions_panel.add_action_btn.clicked.connect(self.add_action)
        self.actions_panel.edit_action_btn.clicked.connect(self.edit_action)
        self.actions_panel.remove_action_btn.clicked.connect(self.remove_action)
        self.actions_panel.up_btn.clicked.connect(lambda: self.move_action(-1))
        self.actions_panel.down_btn.clicked.connect(lambda: self.move_action(1))

        self.preview_panel = PreviewPanel()

        self.left_layout.addWidget(self.profiles_panel)
        self.left_layout.addWidget(self.apps_panel)
        self.left_layout.addStretch(1)

        self.center_layout.addWidget(self.details_card)
        self.center_layout.addWidget(self.actions_panel)
        self.center_layout.addStretch(1)

        self.right_layout.addWidget(self.preview_panel)

        self.content_layout.addWidget(self.left_panel)
        self.content_layout.addWidget(self.center_panel)
        self.content_layout.addWidget(self.right_panel)
        self.content_layout.setStretch(0, 1)
        self.content_layout.setStretch(1, 2)
        self.content_layout.setStretch(2, 1)

        root.addWidget(self.content)
        central.setLayout(root)
        self.setCentralWidget(central)

        self._apply_responsive_layout(self.width())

    def _setup_tray(self) -> None:
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "icon.svg"
        icon = QIcon(str(icon_path)) if icon_path.exists() else self.windowIcon()
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("WinPos")

        menu = QMenu()
        show_action = QAction("Открыть/скрыть", self)
        show_action.triggered.connect(self.toggle_visibility)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self._quit_app)
        menu.addAction(show_action)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        self._apply_responsive_layout(event.size().width())
        super().resizeEvent(event)

    def _apply_responsive_layout(self, width: int) -> None:
        vertical = width < 1100
        if vertical == self._is_vertical:
            return
        self._is_vertical = vertical
        self.content_layout.setDirection(
            QBoxLayout.TopToBottom if vertical else QBoxLayout.LeftToRight
        )
        if vertical:
            self.left_panel.setMaximumWidth(16777215)
        else:
            self.left_panel.setMaximumWidth(380)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_visibility()

    def toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._allow_close:
            event.accept()
            super().closeEvent(event)
            return
        if hasattr(self, "tray") and self.tray.isVisible():
            event.ignore()
            self.hide()
            return
        super().closeEvent(event)

    def _quit_app(self) -> None:
        self._allow_close = True
        if hasattr(self, "tray"):
            self.tray.hide()
        from PySide6.QtWidgets import QApplication

        self.close()
        app = QApplication.instance()
        if app:
            app.quit()

    def _refresh_profiles(self) -> None:
        profiles = list((self.data.get("profiles") or {}).keys())
        if not profiles:
            profiles = ["default"]
            self.data.setdefault("profiles", {})["default"] = {"apps": []}
        self.profiles_panel.profile_combo.clear()
        self.profiles_panel.profile_combo.addItems(profiles)
        default_profile = self.data.get("settings", {}).get("default_profile", profiles[0])
        if default_profile in profiles:
            self.profiles_panel.profile_combo.setCurrentText(default_profile)

    def _refresh_apps(self) -> None:
        self.apps_panel.app_list.clear()
        apps = self.data.get("apps", {})
        for app_id in sorted(apps.keys()):
            self.apps_panel.app_list.addItem(app_id)
        if self.apps_panel.app_list.count() > 0:
            self.apps_panel.app_list.setCurrentRow(0)

    def _on_profile_changed(self, profile_id: str) -> None:
        settings = self.data.setdefault("settings", {})
        settings["default_profile"] = profile_id
        self._refresh_apps()

    def _on_app_selected(self) -> None:
        item = self.apps_panel.app_list.currentItem()
        if not item:
            return
        app_id = item.text()
        app = (self.data.get("apps") or {}).get(app_id, {})
        self.details_card.display_name.setText(app.get("display_name", ""))
        self.details_card.cmd.setText((app.get("launch") or {}).get("cmd", ""))
        match = app.get("window_match", {})
        match_text = ", ".join(f"{k}={v}" for k, v in match.items()) if match else "—"
        self.details_card.match.setText(match_text)
        self._refresh_actions(app)
        self._update_preview(app)

    def _refresh_actions(self, app: Dict[str, Any]) -> None:
        self.actions_panel.action_list.clear()
        for action in app.get("actions", []) or []:
            label = self._format_action(action)
            self.actions_panel.action_list.addItem(label)

    def _format_action(self, action: Dict[str, Any]) -> str:
        params = action.get("params") or {}
        summary = ""
        if params:
            summary = ", ".join(f"{k}={v}" for k, v in params.items())
        action_type = action.get("type", "")
        label = ACTION_DEFS.get(action_type, {}).get("label", action_type)
        return f"{label} {summary}".strip()

    def _update_preview(self, app: Dict[str, Any]) -> None:
        actions = app.get("actions", []) or []
        lines: List[str] = []
        for action in actions:
            if action.get("type") == "use_chain":
                name = (action.get("params") or {}).get("name")
                lines.append(f"use_chain: {name}")
                chain = (self.data.get("action_chains") or {}).get(name, [])
                for chain_action in chain:
                    lines.append(f"  - {self._format_action(chain_action)}")
            else:
                lines.append(f"- {self._format_action(action)}")
        self.preview_panel.preview_box.setPlainText("\n".join(lines) if lines else "Нет действий")

    def add_app(self) -> None:
        dialog = AppDialog()
        result = dialog.get_data()
        if not result:
            return
        app_id = result["app_id"]
        self.data.setdefault("apps", {})[app_id] = result["data"]
        self._refresh_apps()

    def edit_app(self) -> None:
        item = self.apps_panel.app_list.currentItem()
        if not item:
            return
        app_id = item.text()
        app = (self.data.get("apps") or {}).get(app_id, {})
        dialog = AppDialog(app_id=app_id, data=app)
        result = dialog.get_data()
        if not result:
            return
        self.data.setdefault("apps", {})[app_id] = result["data"]
        self._refresh_apps()

    def remove_app(self) -> None:
        item = self.apps_panel.app_list.currentItem()
        if not item:
            return
        app_id = item.text()
        apps = self.data.get("apps", {})
        if app_id in apps:
            del apps[app_id]
        for profile in (self.data.get("profiles") or {}).values():
            if app_id in profile.get("apps", []):
                profile["apps"] = [a for a in profile.get("apps", []) if a != app_id]
        self._refresh_apps()

    def _current_app(self) -> Dict[str, Any]:
        item = self.apps_panel.app_list.currentItem()
        if not item:
            return {}
        app_id = item.text()
        return (self.data.get("apps") or {}).get(app_id, {})

    def add_action(self) -> None:
        app = self._current_app()
        if not app:
            return
        dialog = ActionDialog(
            monitor_roles=self._build_monitor_role_options(),
            chain_names=list((self.data.get("action_chains") or {}).keys()),
        )
        action = dialog.get_action()
        if not action:
            return
        app.setdefault("actions", []).append(action)
        self._refresh_actions(app)
        self._update_preview(app)

    def edit_action(self) -> None:
        app = self._current_app()
        if not app:
            return
        row = self.actions_panel.action_list.currentRow()
        if row < 0:
            return
        actions = app.get("actions", [])
        dialog = ActionDialog(
            action=actions[row],
            monitor_roles=self._build_monitor_role_options(),
            chain_names=list((self.data.get("action_chains") or {}).keys()),
        )
        action = dialog.get_action()
        if not action:
            return
        actions[row] = action
        self._refresh_actions(app)
        self._update_preview(app)

    def remove_action(self) -> None:
        app = self._current_app()
        if not app:
            return
        row = self.actions_panel.action_list.currentRow()
        if row < 0:
            return
        actions = app.get("actions", [])
        actions.pop(row)
        self._refresh_actions(app)
        self._update_preview(app)

    def move_action(self, direction: int) -> None:
        app = self._current_app()
        if not app:
            return
        row = self.actions_panel.action_list.currentRow()
        if row < 0:
            return
        actions = app.get("actions", [])
        new_index = row + direction
        if new_index < 0 or new_index >= len(actions):
            return
        actions[row], actions[new_index] = actions[new_index], actions[row]
        self._refresh_actions(app)
        self.actions_panel.action_list.setCurrentRow(new_index)
        self._update_preview(app)

    def add_profile(self) -> None:
        name, ok = _prompt_text(self, "Новый профиль", "ID профиля")
        if not ok or not name:
            return
        profiles = self.data.setdefault("profiles", {})
        profiles[name] = {"apps": []}
        self._refresh_profiles()

    def edit_profile(self) -> None:
        profile_id = self.profiles_panel.profile_combo.currentText()
        if not profile_id:
            return
        profiles = self.data.setdefault("profiles", {})
        profile = profiles.get(profile_id, {"apps": []})
        apps = sorted((self.data.get("apps") or {}).keys())
        dialog = ProfileDialog(profile_id, apps, profile)
        result = dialog.get_profile()
        if not result:
            return
        profiles[profile_id] = result
        self._refresh_profiles()

    def save_config(self) -> None:
        issues = self.store.validate(self.data)
        if issues:
            QMessageBox.warning(self, "Ошибка", "; ".join(issues))
            return
        self.store.save(self.data)
        QMessageBox.information(self, "Сохранено", "Конфигурация сохранена")

    def validate_config(self) -> None:
        issues = self.store.validate(self.data)
        if issues:
            QMessageBox.warning(self, "Проверка", "; ".join(issues))
        else:
            QMessageBox.information(self, "Проверка", "Ошибок не найдено")

    def _build_monitor_role_options(self) -> List[Dict[str, str]]:
        roles = []
        role_map = self.data.setdefault("monitor_roles", {})
        manager = MonitorManager(role_map)
        try:
            manager.refresh()
        except Exception:
            manager = None
        if manager:
            existing_indexes = {
                cfg.get("match", {}).get("index")
                for cfg in role_map.values()
                if isinstance(cfg, dict)
            }
            for monitor in manager.get_all():
                if monitor.index in existing_indexes:
                    continue
                role_name = f"monitor_{monitor.index + 1}"
                if role_name not in role_map:
                    role_map[role_name] = {"match": {"index": monitor.index}}
        for role, cfg in role_map.items():
            label = role
            if manager:
                monitor = manager.get_by_role(role)
                if monitor:
                    label = f"{monitor.name} ({monitor.width}x{monitor.height})"
                else:
                    label = "Монитор не найден"
            roles.append({"label": label, "value": role})
        return roles


def _prompt_text(parent: QWidget, title: str, label: str) -> tuple[str, bool]:
    from PySide6.QtWidgets import QInputDialog

    text, ok = QInputDialog.getText(parent, title, label)
    return text.strip(), bool(ok)
