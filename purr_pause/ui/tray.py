from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMenu,
    QSystemTrayIcon, QWidget, QWidgetAction,
)

from purr_pause.version import VERSION


def _make_cat_icon() -> QIcon:
    px = QPixmap(QSize(32, 32))
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setFont(QFont("Segoe UI Emoji", 20))
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "🐱")
    painter.end()
    return QIcon(px)


def _make_header_icon(size: int = 22) -> QPixmap:
    px = QPixmap(QSize(size, size))
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setFont(QFont("Segoe UI Emoji", int(size * 0.75)))
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "🐱")
    painter.end()
    return px


def _make_header(menu: QMenu) -> QWidgetAction:
    """Create a non-clickable app header for the top of the context menu."""
    widget = QWidget()
    widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    outer = QHBoxLayout(widget)
    outer.setContentsMargins(18, 10, 18, 10)
    outer.setSpacing(12)

    icon = QLabel()
    icon.setPixmap(_make_header_icon())
    icon.setStyleSheet("background: transparent;")
    outer.addWidget(icon)

    title = QLabel("Purr Pause")
    title.setStyleSheet(
        "color: #F5F5F5; font-size: 14px; font-weight: 600; background: transparent;"
    )
    outer.addWidget(title)
    outer.addStretch()

    action = QWidgetAction(menu)
    action.setDefaultWidget(widget)
    return action


class TrayIcon(QSystemTrayIcon):
    pause_toggle_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, is_paused: bool = False, parent=None):
        super().__init__(_make_cat_icon(), parent)

        menu = QMenu()
        menu.setMinimumWidth(240)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1F1F1F;
                color: #F5F5F5;
                border: 1px solid #333333;
                border-radius: 10px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 10px 24px 10px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(255,255,255,0.08);
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333333;
                margin: 6px 12px;
            }
        """)

        menu.addAction(_make_header(menu))
        menu.addSeparator()

        self._pause_action = menu.addAction("")
        self.set_paused(is_paused)
        self._pause_action.triggered.connect(lambda: self.pause_toggle_requested.emit())

        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(lambda: self.settings_requested.emit())

        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(lambda: self.quit_requested.emit())

        self.setContextMenu(menu)
        self.setToolTip(f"Purr Pause v{VERSION}")
        self.show()

    def set_paused(self, paused: bool) -> None:
        self._pause_action.setText("继续" if paused else "暂停")
