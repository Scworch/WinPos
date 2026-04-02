"""Reusable Material You components."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QPushButton, QVBoxLayout


PRIMARY = QColor("#3A86FF")
SHADOW = QColor(0, 0, 0, 60)


def _build_shadow(blur: float, offset_y: float, color: QColor) -> QGraphicsDropShadowEffect:
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(QPointF(0, offset_y))
    effect.setColor(color)
    return effect


class MaterialCard(QFrame):
    """Rounded card with animated shadow and inner surface."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("MaterialCard")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._shadow = _build_shadow(18, 4, SHADOW)
        self.setGraphicsEffect(self._shadow)
        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._blur_anim.setDuration(180)
        self._blur_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._offset_anim = QPropertyAnimation(self._shadow, b"offset")
        self._offset_anim.setDuration(180)
        self._offset_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.surface = QFrame()
        self.surface.setObjectName("CardSurface")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.addWidget(self.surface)

        self.body = QVBoxLayout(self.surface)
        self.body.setContentsMargins(16, 16, 16, 16)
        self.body.setSpacing(10)

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._animate_shadow(26, 8)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._animate_shadow(18, 4)
        super().leaveEvent(event)

    def _animate_shadow(self, blur: float, offset_y: float) -> None:
        self._blur_anim.stop()
        self._offset_anim.stop()
        self._blur_anim.setStartValue(self._shadow.blurRadius())
        self._blur_anim.setEndValue(blur)
        self._offset_anim.setStartValue(self._shadow.offset())
        self._offset_anim.setEndValue(QPointF(0, offset_y))
        self._blur_anim.start()
        self._offset_anim.start()


class MaterialButton(QPushButton):
    """Pill button with hover/press animation."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("MaterialButton")
        self._shadow = _build_shadow(10, 2, SHADOW)
        self.setGraphicsEffect(self._shadow)
        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._blur_anim.setDuration(140)
        self._blur_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._offset_anim = QPropertyAnimation(self._shadow, b"offset")
        self._offset_anim.setDuration(140)
        self._offset_anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._shadow.setColor(PRIMARY)
        self._animate_shadow(18, 6)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._shadow.setColor(SHADOW)
        self._animate_shadow(10, 2)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self._shadow.setColor(PRIMARY)
        self._animate_shadow(6, 1)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._animate_shadow(18, 6 if self.underMouse() else 2)
        super().mouseReleaseEvent(event)

    def _animate_shadow(self, blur: float, offset_y: float) -> None:
        self._blur_anim.stop()
        self._offset_anim.stop()
        self._blur_anim.setStartValue(self._shadow.blurRadius())
        self._blur_anim.setEndValue(blur)
        self._offset_anim.setStartValue(self._shadow.offset())
        self._offset_anim.setEndValue(QPointF(0, offset_y))
        self._blur_anim.start()
        self._offset_anim.start()
