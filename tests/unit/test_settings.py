import json
import pytest
from pathlib import Path


from purr_pause.infrastructure.config_store import ConfigStore


@pytest.fixture
def cfg(tmp_path):
    default = tmp_path / "config.default.json"
    default.write_text(json.dumps({"interval_minutes": 20, "cat_image_path": ""}), encoding="utf-8")
    return ConfigStore(tmp_path / "config.json", default)


def test_load_config_copies_default_when_missing(cfg):
    config = cfg.load()
    assert config["interval_minutes"] == 20
    assert cfg.config_path.exists()


def test_load_config_reads_existing_file(cfg):
    cfg.save({"interval_minutes": 30, "cat_image_path": ""})
    assert cfg.load()["interval_minutes"] == 30


def test_save_config_persists(cfg):
    cfg.load()
    cfg.save({"interval_minutes": 15, "cat_image_path": ""})
    raw = json.loads(cfg.config_path.read_text(encoding="utf-8"))
    assert raw["interval_minutes"] == 15


def test_settings_dialog_shows_current_interval(qtbot):
    from purr_pause.ui.settings_dialog import SettingsDialog
    dialog = SettingsDialog(current_interval=25)
    qtbot.addWidget(dialog)

    assert dialog.spinbox.value() == 25


def test_settings_dialog_emits_interval_changed_on_save(qtbot):
    from purr_pause.ui.settings_dialog import SettingsDialog
    dialog = SettingsDialog(current_interval=20)
    qtbot.addWidget(dialog)
    dialog.spinbox.setValue(35)

    with qtbot.waitSignal(dialog.saved, timeout=500) as blocker:
        dialog._save()

    assert blocker.args == [35, 20]


def test_settings_dialog_cancel_does_not_emit(qtbot):
    from purr_pause.ui.settings_dialog import SettingsDialog
    dialog = SettingsDialog(current_interval=20)
    qtbot.addWidget(dialog)

    with qtbot.assertNotEmitted(dialog.saved, wait=100):
        dialog.reject()



def test_settings_dialog_shows_current_rest_duration(qtbot):
    from purr_pause.ui.settings_dialog import SettingsDialog
    dialog = SettingsDialog(current_interval=20, current_rest_duration=30)
    qtbot.addWidget(dialog)

    assert dialog.rest_spinbox.value() == 30


def test_settings_dialog_emits_rest_duration_changed_on_save(qtbot):
    from purr_pause.ui.settings_dialog import SettingsDialog
    dialog = SettingsDialog(current_interval=20, current_rest_duration=20)
    qtbot.addWidget(dialog)
    dialog.rest_spinbox.setValue(35)

    with qtbot.waitSignal(dialog.saved, timeout=500) as blocker:
        dialog._save()

    assert blocker.args == [20, 35]
