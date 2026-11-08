import pytest

from purr_pause.ui.tray import TrayIcon


@pytest.mark.parametrize("label,signal", [
    ("暂停", "pause_toggle_requested"),
    ("设置", "settings_requested"),
    ("退出", "quit_requested"),
])
def test_menu_actions_emit_intent_without_performing_business_work(qtbot, label, signal):
    tray = TrayIcon()
    try:
        action = next(action for action in tray.contextMenu().actions() if action.text() == label)
        with qtbot.waitSignal(getattr(tray, signal)):
            action.trigger()
        assert tray._pause_action.text() == "暂停"
    finally:
        tray.deleteLater()


def test_initial_and_explicit_pause_state_control_menu_text(qtbot):
    tray = TrayIcon(is_paused=True)
    try:
        assert tray._pause_action.text() == "继续"
        tray.set_paused(False)
        assert tray._pause_action.text() == "暂停"
    finally:
        tray.deleteLater()
