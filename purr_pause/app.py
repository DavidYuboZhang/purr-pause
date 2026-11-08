"""Application composition root."""
import sys

from PyQt6.QtWidgets import QApplication

from purr_pause.controller import ApplicationController
from purr_pause.core.timer import RestTimer
from purr_pause.infrastructure.config_store import ConfigStore
from purr_pause.infrastructure.paths import resource_path, user_data_dir
from purr_pause.rest_session import RestSession
from purr_pause.ui.tray import TrayIcon


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    store = ConfigStore(user_data_dir() / "config.json", resource_path("config/config.default.json"))
    config = store.load()
    timer = RestTimer(interval_minutes=config["interval_minutes"])
    tray = TrayIcon(is_paused=timer.is_paused)
    session = RestSession(resource_path("assets/cat_anim"))
    controller = ApplicationController(timer, store, tray, session)  # Keep alive through exec().
    tray.quit_requested.connect(app.quit)
    app.aboutToQuit.connect(timer.pause)
    app.aboutToQuit.connect(session.close)
    timer.start()
    return app.exec()
