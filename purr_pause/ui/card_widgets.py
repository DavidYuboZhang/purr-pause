"""Rest-card drawing components and unchanged visual constants."""
from purr_pause.infrastructure.paths import resource_path
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, pyqtProperty, QSequentialAnimationGroup,
    QEasingCurve, QRectF,
)
from PyQt6.QtGui import (
    QBrush, QColor, QFontDatabase, QLinearGradient,
    QPainterPath, QPixmap, QPainter,
)
from PyQt6.QtWidgets import QWidget

THUMB_SIZE    = 80
CARD_W        = 360
CARD_H        = 120
SHADOW_MARGIN = 20          # transparent border around card for shadow bleed
WIN_W         = CARD_W + 2 * SHADOW_MARGIN
WIN_H         = CARD_H + 2 * SHADOW_MARGIN
MARGIN_EDGE   = 16          # gap between card edge and screen edge
GLOW_MARGIN   = 12          # max glow spread (px); must be ≤ SHADOW_MARGIN
_STATIC_EXTS  = {".png", ".jpg", ".jpeg", ".webp"}

_CARD_FILL = QColor(0, 0, 0, 255)   # pure black — matches Mascot Cat Black.png background

_NOTO_FAMILY: str | None = None


def _make_circular_pixmap(px: QPixmap, size: int) -> QPixmap:
    """Clip pixmap to a circle."""
    result = QPixmap(size, size)
    result.fill(Qt.GlobalColor.transparent)
    p = QPainter(result)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0.0, 0.0, float(size), float(size))
    p.setClipPath(path)
    scaled = px.scaled(size, size,
                       Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                       Qt.TransformationMode.SmoothTransformation)
    p.drawPixmap(0, 0, scaled)
    p.end()
    return result



def _ensure_font() -> str:
    """Load Noto Sans SC variable font once; fall back to Microsoft YaHei."""
    global _NOTO_FAMILY
    if _NOTO_FAMILY is None:
        font_path = resource_path("assets/fonts/NotoSansSC[wght].ttf")
        if font_path.exists():
            fid = QFontDatabase.addApplicationFont(str(font_path))
            families = QFontDatabase.applicationFontFamilies(fid)
            if families:
                _NOTO_FAMILY = families[0]
        if _NOTO_FAMILY is None:
            _NOTO_FAMILY = "Microsoft YaHei"
    return _NOTO_FAMILY


class _ProgressBar(QWidget):
    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self._total = total
        self._remaining = total
        self.setFixedHeight(4)

    def set_remaining(self, remaining: int) -> None:
        self._remaining = remaining
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        # Track
        p.setBrush(QColor(255, 255, 255, 38))
        p.drawRoundedRect(self.rect(), 2, 2)
        # Amber gradient fill
        ratio = self._remaining / self._total if self._total > 0 else 0
        fill_w = int(self.width() * ratio)
        if fill_w > 0:
            r = self.rect()
            r.setWidth(fill_w)
            grad = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0.0, QColor(0xFF, 0x9F, 0x0A))  # #FF9F0A
            grad.setColorAt(1.0, QColor(0xFF, 0xCC, 0x02))  # #FFCC02
            p.setBrush(grad)
            p.drawRoundedRect(r, 2, 2)
        p.end()


class _GlowCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._glow: float = 0.4
        self._anim_group: QSequentialAnimationGroup | None = None
        self.setFixedSize(CARD_W + 2 * GLOW_MARGIN, CARD_H + 2 * GLOW_MARGIN)

    @pyqtProperty(float)
    def glow_intensity(self) -> float:
        return self._glow

    @glow_intensity.setter
    def glow_intensity(self, value: float) -> None:
        self._glow = value
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)

        card_r = QRectF(self.rect()).adjusted(
            GLOW_MARGIN, GLOW_MARGIN, -GLOW_MARGIN, -GLOW_MARGIN
        )

        # Outer glow layers (amber, alpha scales with glow_intensity)
        for spread, base_alpha in ((12, 40), (7, 65), (3, 90)):
            gr = card_r.adjusted(-spread, -spread, spread, spread)
            p.setBrush(QColor(0xFF, 0x9F, 0x0A, int(base_alpha * self._glow)))
            p.drawRoundedRect(gr, 16 + spread * 0.6, 16 + spread * 0.6)

        # Gradient border fill (amber → gold), leaves ~2px ring after fill is drawn on top
        grad = QLinearGradient(card_r.topLeft(), card_r.bottomRight())
        grad.setColorAt(0.0, QColor(0xFF, 0x9F, 0x0A))
        grad.setColorAt(1.0, QColor(0xFF, 0xCC, 0x02))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(card_r, 16.0, 16.0)

        # Inner card fill covers border, leaving a ~2px gradient ring visible
        p.setBrush(_CARD_FILL)
        p.drawRoundedRect(card_r.adjusted(2, 2, -2, -2), 14.0, 14.0)

        p.end()

    def start_breathing(self) -> None:
        if self._anim_group is not None:
            self._anim_group.stop()
        fwd = QPropertyAnimation(self, b"glow_intensity")
        fwd.setDuration(1200)
        fwd.setStartValue(0.4)
        fwd.setEndValue(1.0)
        fwd.setEasingCurve(QEasingCurve.Type.InOutSine)

        bwd = QPropertyAnimation(self, b"glow_intensity")
        bwd.setDuration(1200)
        bwd.setStartValue(1.0)
        bwd.setEndValue(0.4)
        bwd.setEasingCurve(QEasingCurve.Type.InOutSine)

        self._anim_group = QSequentialAnimationGroup(self)
        self._anim_group.addAnimation(fwd)
        self._anim_group.addAnimation(bwd)
        self._anim_group.setLoopCount(-1)
        self._anim_group.start()

    def stop_breathing(self) -> None:
        if self._anim_group is not None:
            self._anim_group.stop()
