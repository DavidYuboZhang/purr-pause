"""Own the windows and lifetime of one rest reminder."""
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from purr_pause.ui.animation_window import CatAnimWindow
from purr_pause.ui.rest_card import CatWindow


class RestSession(QObject):
    finished = pyqtSignal()

    def __init__(self, sprite_dir: Path, card_factory=CatWindow,
                 animation_factory=CatAnimWindow, parent=None):
        super().__init__(parent)
        self._sprite_dir = Path(sprite_dir)
        self._card_factory = card_factory
        self._animation_factory = animation_factory
        self._windows = {}

    @property
    def is_active(self) -> bool:
        return bool(self._windows)

    def start(self, config: dict) -> bool:
        if self.is_active:
            return False
        duration = config.get("rest_duration_seconds", 20)
        card = self._card_factory(
            image_path=config.get("cat_image_path", ""), rest_duration=duration,
        )
        self._track(card)
        if (self._sprite_dir / "manifest.json").exists():
            animation = self._animation_factory(
                self._sprite_dir, rest_duration_seconds=duration,
            )
            self._track(animation)
            card.countdown_finished.connect(animation.request_finish)
            animation.show()
        card.show()
        return True

    def close(self) -> None:
        for window in list(self._windows.values()):
            window.close()

    def _track(self, window) -> None:
        key = id(window)
        self._windows[key] = window
        window.destroyed.connect(lambda _obj=None, key=key: self._on_destroyed(key))

    def _on_destroyed(self, key: int) -> None:
        if key in self._windows:
            del self._windows[key]
            if not self._windows:
                self.finished.emit()
