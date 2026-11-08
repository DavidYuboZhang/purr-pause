from pathlib import Path

from purr_pause.infrastructure.paths import resource_path
from PyQt6.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, pyqtSignal,
    QParallelAnimationGroup, QEasingCurve, QPoint,
)
from PyQt6.QtGui import (
    QFont, QMovie, QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from purr_pause.ui.card_widgets import (
    _ProgressBar, _GlowCard, _make_circular_pixmap, _ensure_font,
    THUMB_SIZE, CARD_W, SHADOW_MARGIN, WIN_W, WIN_H,
    MARGIN_EDGE, GLOW_MARGIN, _STATIC_EXTS,
)


class CatWindow(QWidget):
    countdown_finished = pyqtSignal()

    def __init__(self, image_path: str = "", rest_duration: int = 20):
        super().__init__()
        self._image_path = image_path
        self._countdown = rest_duration
        self._anim = None
        self._movie = None
        self._entry_anim = None
        self._glow_card: _GlowCard | None = None
        self._setup_window()
        self._setup_ui()
        self._start_countdown()

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Delete the widget on close so rest cards don't pile up in memory; the
        # rest session relies on the destroyed signal to clean up.
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFixedSize(WIN_W, WIN_H)
        screen = QApplication.primaryScreen().availableGeometry()
        # card's visible right/top edges land at MARGIN_EDGE from screen edges
        self._target_x = screen.right() - CARD_W - MARGIN_EDGE - SHADOW_MARGIN
        self._target_y = screen.top() + MARGIN_EDGE - SHADOW_MARGIN
        self.move(self._target_x, screen.top() - WIN_H)
        self.setWindowOpacity(0.0)

    def _setup_ui(self) -> None:
        fam = _ensure_font()

        # ── 左侧：猫咪缩略图（圆形）──────────────────────────
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gif_label.setFixedSize(THUMB_SIZE, THUMB_SIZE)
        gif_label.setStyleSheet(
            f"border-radius: {THUMB_SIZE // 2}px;"
            " background: #000000;"
        )

        _DEFAULT_STATIC = resource_path("assets/Mascot Cat Black.png")
        custom = Path(self._image_path) if self._image_path else Path()
        if custom.exists() and custom.suffix.lower() in _STATIC_EXTS:
            src = custom
        elif _DEFAULT_STATIC.exists():
            src = _DEFAULT_STATIC
        else:
            src = None

        if src is not None:
            gif_label.setPixmap(
                _make_circular_pixmap(QPixmap(str(src)), THUMB_SIZE)
            )
        else:
            gif_path = (
                custom if custom.exists() and custom.suffix.lower() == ".gif"
                else resource_path("assets/cat.gif")
            )
            self._movie = QMovie(str(gif_path))
            self._movie.jumpToFrame(0)
            nat = self._movie.currentImage().size()
            if nat.isValid() and nat.width() > 0 and nat.height() > 0:
                scale = min(THUMB_SIZE / nat.width(), THUMB_SIZE / nat.height())
                scaled = QSize(int(nat.width() * scale), int(nat.height() * scale))
            else:
                scaled = QSize(THUMB_SIZE, THUMB_SIZE)
            self._movie.setScaledSize(scaled)
            gif_label.setMovie(self._movie)
            self._movie.start()

        # ── 中列：垂直居中的倒计时 + 进度条 ──────────────────────
        f_count = QFont(fam, 26)
        f_count.setWeight(QFont.Weight.Medium)
        self._time_label = QLabel(self._fmt_countdown())
        self._time_label.setFont(f_count)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_label.setStyleSheet("color: white;")

        self._progress_bar = _ProgressBar(total=self._countdown)

        center_col = QVBoxLayout()
        center_col.setSpacing(6)
        center_col.setContentsMargins(0, 0, 0, 0)
        center_col.addStretch(1)
        center_col.addWidget(self._time_label)
        center_col.addWidget(self._progress_bar)
        center_col.addStretch(1)

        # ── 右列：关闭按钮顶部对齐 ────────────────────────────────
        close_btn = QPushButton("×")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.20); border: none;"
            " color: white; font-size: 13px; border-radius: 11px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.35); }"
        )
        close_btn.clicked.connect(self._dismiss)

        close_col = QVBoxLayout()
        close_col.setContentsMargins(0, 0, 0, 0)
        close_col.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)
        close_col.addStretch()

        # ── 卡片容器（_GlowCard 包含发光边框 + 内填充） ─────────
        self._glow_card = _GlowCard()
        inner_layout = QHBoxLayout()
        inner_layout.setContentsMargins(
            GLOW_MARGIN + 12, GLOW_MARGIN + 12,
            GLOW_MARGIN + 12, GLOW_MARGIN + 12,
        )
        inner_layout.setSpacing(12)
        inner_layout.addWidget(gif_label)
        inner_layout.addLayout(center_col, 1)   # stretch=1: fills horizontal space
        inner_layout.addLayout(close_col)
        self._glow_card.setLayout(inner_layout)

        # ── 外层透明容器（为发光留白） ────────────────────────────
        outer = QVBoxLayout()
        outer.setContentsMargins(
            SHADOW_MARGIN - GLOW_MARGIN, SHADOW_MARGIN - GLOW_MARGIN,
            SHADOW_MARGIN - GLOW_MARGIN, SHADOW_MARGIN - GLOW_MARGIN,
        )
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._glow_card)
        self.setLayout(outer)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QApplication.primaryScreen().availableGeometry()
        start_pos = QPoint(self._target_x, screen.top() - WIN_H)
        end_pos   = QPoint(self._target_x, self._target_y)

        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(420)
        pos_anim.setStartValue(start_pos)
        pos_anim.setEndValue(end_pos)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutBack)  # spring bounce

        opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        opacity_anim.setDuration(280)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)

        self._entry_anim = QParallelAnimationGroup()
        self._entry_anim.addAnimation(pos_anim)
        self._entry_anim.addAnimation(opacity_anim)
        self._entry_anim.start()
        self._entry_anim.finished.connect(self._glow_card.start_breathing)

    def _fmt_countdown(self) -> str:
        m, s = divmod(self._countdown, 60)
        return f"{m:02d}:{s:02d}"

    def _start_countdown(self) -> None:
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self) -> None:
        self._countdown -= 1
        self._time_label.setText(self._fmt_countdown())
        self._progress_bar.set_remaining(self._countdown)
        if self._countdown <= 0:
            self.countdown_finished.emit()
            self._timer.stop()
            self._fade_out()

    def closeEvent(self, event) -> None:
        self._timer.stop()
        if self._entry_anim is not None:
            self._entry_anim.stop()
        if self._glow_card is not None:
            self._glow_card.stop_breathing()
        super().closeEvent(event)

    def _dismiss(self) -> None:
        self.countdown_finished.emit()
        self._fade_out()

    def _fade_out(self) -> None:
        if self._entry_anim is not None:
            self._entry_anim.stop()
        if self._glow_card is not None:
            self._glow_card.stop_breathing()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(500)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.close)
        self._anim.start()
