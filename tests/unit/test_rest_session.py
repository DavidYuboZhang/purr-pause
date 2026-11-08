import pytest
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget

from purr_pause.rest_session import RestSession


class Card(QWidget):
    countdown_finished = pyqtSignal()

    def __init__(self, **config):
        super().__init__()
        self.config = config
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)


class Animation(Card):
    def __init__(self, sprite_dir, **config):
        super().__init__(**config)
        self.requests = 0

    def request_finish(self):
        self.requests += 1


@pytest.fixture
def scene(qtbot, tmp_path):
    (tmp_path / "manifest.json").write_text("{}")
    cards, animations = [], []
    def card_factory(**config):
        card = Card(**config)
        cards.append(card)
        return card
    def animation_factory(*args, **config):
        anim = Animation(*args, **config)
        animations.append(anim)
        return anim
    session = RestSession(tmp_path, card_factory, animation_factory)
    yield session, cards, animations
    session.close()
    qtbot.waitUntil(lambda: not session.is_active, timeout=1000)


def test_session_passes_current_configuration_and_suppresses_duplicates(scene):
    session, cards, animations = scene
    assert session.start({"cat_image_path": "custom.png", "rest_duration_seconds": 30})
    assert session.is_active
    assert cards[0].config == {"image_path": "custom.png", "rest_duration": 30}
    assert animations[0].config == {"rest_duration_seconds": 30}
    assert not session.start({"rest_duration_seconds": 20})
    assert len(cards) == len(animations) == 1


def test_completion_finishes_animation_and_waits_for_both_destructions(scene, qtbot):
    session, cards, animations = scene
    completions = []
    session.finished.connect(lambda: completions.append(True))
    session.start({})
    cards[0].countdown_finished.emit()
    assert animations[0].requests == 1
    cards[0].close()
    qtbot.wait(10)
    assert session.is_active
    assert completions == []
    with qtbot.waitSignal(session.finished, timeout=1000):
        animations[0].close()
    assert not session.is_active
    assert completions == [True]
    assert session.start({})
    assert len(cards) == 2


def test_close_releases_both_windows_and_emits_once(scene, qtbot):
    session, cards, animations = scene
    completions = []
    session.finished.connect(lambda: completions.append(True))
    session.start({})
    with qtbot.waitSignal(session.finished, timeout=1000):
        session.close()
    session.close()
    assert not session.is_active
    assert completions == [True]


def test_missing_manifest_shows_only_card(qtbot, tmp_path):
    def unexpected_animation(*args, **kwargs):
        raise AssertionError("Missing manifest must use the card-only path")
    session = RestSession(tmp_path, Card, unexpected_animation)
    assert session.start({})
    assert session.is_active
    with qtbot.waitSignal(session.finished, timeout=1000):
        session.close()
    assert not session.is_active
