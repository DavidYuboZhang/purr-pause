"""Connect user intent to configuration, work timing and rest sessions."""
from PyQt6.QtCore import QObject

from purr_pause.ui.settings_dialog import SettingsDialog


class ApplicationController(QObject):
    def __init__(self, timer, store, tray, session, dialog_factory=SettingsDialog, parent=None):
        super().__init__(parent)
        self._timer = timer
        self._store = store
        self._tray = tray
        self._session = session
        self._dialog_factory = dialog_factory
        tray.set_paused(timer.is_paused)
        tray.pause_toggle_requested.connect(self.toggle_pause)
        tray.settings_requested.connect(self.open_settings)
        timer.paused_changed.connect(tray.set_paused)
        timer.rest_due.connect(self.on_rest_due)

    def toggle_pause(self) -> None:
        if self._timer.is_paused:
            self._timer.resume()
        else:
            self._timer.pause()

    def open_settings(self) -> None:
        config = self._store.load()
        dialog = self._dialog_factory(
            current_interval=config["interval_minutes"],
            current_rest_duration=config.get("rest_duration_seconds", 20),
        )
        dialog.saved.connect(self.apply_settings)
        dialog.exec()

    def apply_settings(self, minutes: int, seconds: int) -> None:
        config = self._store.load()
        config["interval_minutes"] = minutes
        config["rest_duration_seconds"] = seconds
        self._store.save(config)
        self._timer.reset(minutes)

    def on_rest_due(self) -> None:
        if not self._session.is_active:
            self._session.start(self._store.load())
