"""Shared test isolation: never create desktop tray icons during pytest."""
import pytest

from purr_pause.ui.tray import TrayIcon


@pytest.fixture(autouse=True)
def hide_test_tray_icons(monkeypatch):
    monkeypatch.setattr(TrayIcon, "show", lambda self: None)
