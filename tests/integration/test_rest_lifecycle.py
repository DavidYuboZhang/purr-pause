"""Exercise real card/overlay signals and deferred Qt destruction together."""
import json

import pytest
from PIL import Image
from PyQt6 import sip
from PyQt6.QtWidgets import QPushButton

from purr_pause.rest_session import RestSession
from purr_pause.ui.animation_window import CatAnimWindow
from purr_pause.ui.rest_card import CatWindow


@pytest.mark.parametrize("early_close", [False, True])
def test_real_windows_finish_release_and_allow_next_reminder(qtbot, tmp_path, early_close):
    Image.new("RGBA", (4, 4), (100, 150, 200, 255)).save(tmp_path / "frame_001.png")
    (tmp_path / "manifest.json").write_text(json.dumps({
        "canvas": [100, 50], "frames": [{"x": 0, "y": 0, "t": 0}],
    }))
    windows = []

    def card_factory(**kwargs):
        card = CatWindow(**kwargs)
        windows.append(card)
        return card

    def animation_factory(*args, **kwargs):
        animation = CatAnimWindow(*args, **kwargs)
        windows.append(animation)
        return animation

    session = RestSession(tmp_path, card_factory, animation_factory)
    completions = []
    session.finished.connect(lambda: completions.append(True))
    try:
        assert session.start({"rest_duration_seconds": 1})
        assert not session.start({"rest_duration_seconds": 1})
        if early_close:
            windows[0].findChild(QPushButton).click()
        qtbot.waitUntil(lambda: not session.is_active, timeout=2500)
        assert all(sip.isdeleted(window) for window in windows)
        assert completions == [True]
        assert session.start({"rest_duration_seconds": 1})
        assert len(windows) == 4
    finally:
        session.close()
        qtbot.waitUntil(lambda: not session.is_active, timeout=1000)
    assert all(sip.isdeleted(window) for window in windows)
    assert completions == [True, True]
