import json

import pytest
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QDialog

from purr_pause.controller import ApplicationController
from purr_pause.core.timer import RestTimer
from purr_pause.infrastructure.config_store import ConfigStore


class Tray(QObject):
    pause_toggle_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def set_paused(self, value):
        self.paused = value


class Session:
    is_active = False

    def start(self, config):
        self.config = config
        return True


class CountingStore(ConfigStore):
    writes = 0
    reads = 0

    def load(self):
        self.reads += 1
        return super().load()

    def save(self, config):
        self.writes += 1
        super().save(config)


@pytest.fixture
def flow(qtbot, tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"interval_minutes": 1, "rest_duration_seconds": 20,
                               "cat_image_path": "custom.png", "future": {"x": 1}}))
    store = CountingStore(path, tmp_path / "default.json")
    timer = RestTimer(1)
    timer.start()
    tray, session = Tray(), Session()
    controller = ApplicationController(timer, store, tray, session)
    yield controller, timer, store, tray, session
    timer.pause()


@pytest.mark.parametrize("paused", [False, True])
def test_combined_save_writes_once_preserves_unknown_and_pause(flow, paused):
    controller, timer, store, tray, session = flow
    if paused:
        timer.pause()
    controller.apply_settings(2, 30)
    assert store.writes == 1
    assert store.load() == {"interval_minutes": 2, "rest_duration_seconds": 30,
                            "cat_image_path": "custom.png", "future": {"x": 1}}
    assert timer.is_paused is paused
    assert timer._timer.isActive() is not paused
    assert timer._interval_ms == 120_000
    assert tray.paused is paused


def test_tray_requests_toggle_real_timer_and_sync_label(flow):
    controller, timer, store, tray, session = flow
    tray.pause_toggle_requested.emit()
    assert timer.is_paused and tray.paused
    tray.pause_toggle_requested.emit()
    assert not timer.is_paused and not tray.paused


def test_active_rest_does_not_load_config_or_create_another_session(flow):
    controller, timer, store, tray, session = flow
    session.is_active = True
    timer.rest_due.emit()
    assert store.reads == 0
    assert not hasattr(session, "config")


def test_new_reminder_reads_latest_persisted_configuration(flow):
    controller, timer, store, tray, session = flow
    config = store.load()
    config["rest_duration_seconds"] = 35
    store.save(config)
    timer.rest_due.emit()
    assert session.config["rest_duration_seconds"] == 35
    assert session.config["cat_image_path"] == "custom.png"


def test_save_failure_propagates_before_timer_reset(flow, monkeypatch):
    controller, timer, store, tray, session = flow
    original = store.config_path.read_bytes()
    def fail(config):
        raise OSError("test write failure")
    monkeypatch.setattr(store, "save", fail)
    with pytest.raises(OSError, match="test write failure"):
        controller.apply_settings(2, 30)
    assert timer._interval_ms == 60_000
    assert store.config_path.read_bytes() == original


def test_cancelled_dialog_does_not_save_or_reset(flow):
    controller, timer, store, tray, session = flow
    initial = store.config_path.read_bytes()
    class CancelDialog(QObject):
        saved = pyqtSignal(int, int)
        def __init__(self, **values):
            super().__init__()
            assert values == {"current_interval": 1, "current_rest_duration": 20}
        def exec(self):
            return QDialog.DialogCode.Rejected
    controller._dialog_factory = CancelDialog
    tray.settings_requested.emit()
    assert store.writes == 0
    assert store.config_path.read_bytes() == initial
    assert timer._timer.isActive()
