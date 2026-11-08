from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class RestTimer(QObject):
    rest_due = pyqtSignal()
    paused_changed = pyqtSignal(bool)

    def __init__(self, interval_minutes: int = 20):
        super().__init__()
        self._interval_ms = int(interval_minutes * 60 * 1000)
        self._paused = False
        self._timer = QTimer()
        self._timer.timeout.connect(self.rest_due)

    def start(self) -> None:
        if not self._paused:
            self._timer.start(self._interval_ms)

    def pause(self) -> None:
        self._timer.stop()
        if not self._paused:
            self._paused = True
            self.paused_changed.emit(True)

    def resume(self) -> None:
        if self._paused:
            self._paused = False
            self.start()
            self.paused_changed.emit(False)

    def reset(self, interval_minutes: int) -> None:
        self._interval_ms = int(interval_minutes * 60 * 1000)
        self._timer.stop()
        self.start()

    @property
    def is_paused(self) -> bool:
        return self._paused
