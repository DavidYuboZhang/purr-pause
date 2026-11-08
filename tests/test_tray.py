import json

import pytest

import settings
from timer import RestTimer
from tray import TrayIcon


@pytest.fixture(autouse=True)
def hide_test_tray_icons(monkeypatch):
    monkeypatch.setattr(TrayIcon, "show", lambda self: None)


@pytest.fixture
def tray_with_config(qtbot, tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"interval_minutes": 1, "rest_duration_seconds": 20, "cat_image_path": ""}),
        encoding="utf-8",
    )
    monkeypatch.setattr(settings, "CONFIG_PATH", config_path)
    timer = RestTimer(interval_minutes=1)
    timer.start()
    tray = TrayIcon(timer)
    yield timer, tray, config_path
    timer.pause()
    tray.hide()
    tray.deleteLater()


def save_dialog_values(monkeypatch, minutes, seconds):
    # Replace only the modal UI boundary; production signal wiring and save
    # handlers still run through TrayIcon._open_settings().
    def accept_dialog(dialog):
        dialog.spinbox.setValue(minutes)
        dialog.rest_spinbox.setValue(seconds)
        dialog._save()
        return dialog.result()

    monkeypatch.setattr(settings.SettingsDialog, "exec", accept_dialog)


def test_tray_can_be_instantiated(qtbot):
    timer = RestTimer(interval_minutes=20)
    tray = TrayIcon(timer)
    assert tray is not None
    tray.hide()


def test_tray_toggle_pause_sets_paused(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 60000
    timer.start()
    tray = TrayIcon(timer)

    tray._toggle_pause()
    assert timer.is_paused
    tray.hide()


def test_tray_toggle_pause_twice_resumes(qtbot):
    timer = RestTimer(interval_minutes=20)
    timer._interval_ms = 60000
    timer.start()
    tray = TrayIcon(timer)

    tray._toggle_pause()
    tray._toggle_pause()
    assert not timer.is_paused
    tray.hide()


@pytest.mark.parametrize("minutes,seconds", [(1, 20), (2, 20), (1, 30)])
def test_save_settings_keeps_timer_paused(qtbot, tray_with_config, monkeypatch, minutes, seconds):
    timer, tray, config_path = tray_with_config
    tray._toggle_pause()
    save_dialog_values(monkeypatch, minutes, seconds)

    tray._open_settings()

    assert json.loads(config_path.read_text(encoding="utf-8")) == {
        "interval_minutes": minutes,
        "rest_duration_seconds": seconds,
        "cat_image_path": "",
    }
    assert timer.is_paused
    assert not timer._timer.isActive()
    assert tray._pause_action.text() == "继续"
    with qtbot.assertNotEmitted(timer.rest_due, wait=100):
        pass

    tray._toggle_pause()
    assert not timer.is_paused
    assert timer._timer.isActive()
    assert timer._timer.interval() == minutes * 60_000
    assert tray._pause_action.text() == "暂停"


@pytest.mark.parametrize("minutes,seconds", [(1, 20), (2, 20), (1, 30)])
def test_save_settings_while_running_keeps_timer_running(tray_with_config, monkeypatch, minutes, seconds):
    timer, tray, config_path = tray_with_config
    save_dialog_values(monkeypatch, minutes, seconds)

    tray._open_settings()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["interval_minutes"] == minutes
    assert config["rest_duration_seconds"] == seconds
    assert not timer.is_paused
    assert timer._timer.isActive()
    assert timer._timer.interval() == minutes * 60_000
    assert tray._pause_action.text() == "暂停"


@pytest.mark.parametrize("paused", [False, True])
def test_cancel_settings_keeps_configuration_and_timer_state(tray_with_config, monkeypatch, paused):
    timer, tray, config_path = tray_with_config
    if paused:
        tray._toggle_pause()
    original_bytes = config_path.read_bytes()

    def cancel_dialog(dialog):
        dialog.spinbox.setValue(2)
        dialog.rest_spinbox.setValue(30)
        dialog.reject()
        return dialog.result()

    monkeypatch.setattr(settings.SettingsDialog, "exec", cancel_dialog)
    tray._open_settings()

    assert config_path.read_bytes() == original_bytes
    assert timer.is_paused is paused
    assert timer._timer.isActive() is not paused
    assert tray._pause_action.text() == ("继续" if paused else "暂停")


def test_tray_initial_label_reflects_an_already_paused_timer(qtbot):
    timer = RestTimer(interval_minutes=1)
    timer.pause()

    tray = TrayIcon(timer)
    try:
        assert tray._pause_action.text() == "继续"
    finally:
        tray.hide()
        tray.deleteLater()


def test_tray_label_tracks_direct_timer_state_changes(tray_with_config):
    timer, tray, _ = tray_with_config

    timer.pause()
    assert tray._pause_action.text() == "继续"
    assert not timer._timer.isActive()

    timer.resume()
    assert tray._pause_action.text() == "暂停"
    assert timer._timer.isActive()


def test_repeated_tray_toggles_stay_consistent(tray_with_config):
    timer, tray, _ = tray_with_config
    for paused in [True, False, True, False]:
        tray._toggle_pause()
        assert timer.is_paused is paused
        assert timer._timer.isActive() is not paused
        assert tray._pause_action.text() == ("继续" if paused else "暂停")
