"""Tests for build_dist.py helper functions."""
from pathlib import Path

import pytest

from scripts import build_dist


def test_conda_dll_search_path_is_added_only_to_build_child(monkeypatch, tmp_path):
    dll_dir = tmp_path / "Library" / "bin"
    dll_dir.mkdir(parents=True)
    monkeypatch.setattr(build_dist.sys, "prefix", str(tmp_path))
    monkeypatch.setenv("PATH", "original-path")
    env = build_dist.build_environment()
    expected = [str(dll_dir), "original-path"]
    if build_dist.sys.platform == "win32":
        expected.insert(0, str(Path(build_dist.os.environ["SystemRoot"]) / "System32"))
    assert env["PATH"] == build_dist.os.pathsep.join(expected)
    assert build_dist.os.environ["PATH"] == "original-path"


def test_build_environment_without_conda_dll_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(build_dist.sys, "prefix", str(tmp_path))
    monkeypatch.setenv("PATH", "original-path")
    expected = dict(build_dist.os.environ)
    if build_dist.sys.platform == "win32":
        expected["PATH"] = str(Path(build_dist.os.environ["SystemRoot"]) / "System32") + build_dist.os.pathsep + "original-path"
    assert build_dist.build_environment() == expected


def test_windows_system_dlls_take_priority_over_unrelated_path_entries(monkeypatch, tmp_path):
    monkeypatch.setattr(build_dist.sys, "platform", "win32")
    monkeypatch.setattr(build_dist.sys, "prefix", str(tmp_path / "env"))
    monkeypatch.setenv("SystemRoot", str(tmp_path / "Windows"))
    monkeypatch.setenv("PATH", str(tmp_path / "unrelated-poppler"))
    env = build_dist.build_environment()
    assert env["PATH"].split(build_dist.os.pathsep)[0] == str(tmp_path / "Windows" / "System32")
    assert build_dist.os.environ["PATH"] == str(tmp_path / "unrelated-poppler")


class TestOutputFilename:
    def test_windows(self):
        assert build_dist.output_filename("0.1.0", "win32") == "PurrPause-0.1.0-windows.exe"

    def test_macos(self):
        assert build_dist.output_filename("0.1.0", "darwin") == "PurrPause-0.1.0-macos.dmg"

    def test_unknown_platform_raises(self):
        with pytest.raises(ValueError, match="unsupported"):
            build_dist.output_filename("0.1.0", "linux")


class TestAddDataPairs:
    """Test the separator at the END of each pair, not just `in` — on Windows the
    drive-letter colon (C:/Users/...) means `":" in pair` is trivially true."""

    WIN_ENDINGS = (";config", ";assets", ";assets/cat_anim", ";assets/fonts")
    MAC_ENDINGS = (":config", ":assets", ":assets/cat_anim", ":assets/fonts")

    def test_windows_uses_semicolon(self, tmp_path):
        pairs = build_dist.add_data_pairs(tmp_path, "win32")
        for pair in pairs:
            assert pair.endswith(self.WIN_ENDINGS), f"unexpected ending: {pair}"

    def test_macos_uses_colon(self, tmp_path):
        pairs = build_dist.add_data_pairs(tmp_path, "darwin")
        for pair in pairs:
            assert pair.endswith(self.MAC_ENDINGS), f"unexpected ending: {pair}"

    def test_includes_all_required_assets(self, tmp_path):
        pairs = build_dist.add_data_pairs(tmp_path, "win32")
        joined = " ".join(pairs)
        assert "config.default.json" in joined
        assert "cat_anim" in joined
        assert "cat.gif" in joined
        assert "NotoSansSC" in joined


class TestEmojiFontPath:
    def test_windows(self):
        p = build_dist.emoji_font_path("win32")
        assert str(p) == "C:/Windows/Fonts/seguiemj.ttf"

    def test_macos(self):
        p = build_dist.emoji_font_path("darwin")
        assert str(p) == "/System/Library/Fonts/Apple Color Emoji.ttc"

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            build_dist.emoji_font_path("linux")


class TestMacOSBranch:
    def test_make_icns_uses_apple_color_emoji_font(self, monkeypatch):
        """Verifies make_icns reads from emoji_font_path('darwin'), not Windows path."""
        captured = []
        from PIL import ImageFont

        def fake_truetype(path, size):
            captured.append(str(path))
            # Return a real font so the rest of make_icns can proceed if reached.
            raise RuntimeError("font-not-loaded (test stub)")

        monkeypatch.setattr(ImageFont, "truetype", fake_truetype)

        with pytest.raises(RuntimeError):
            build_dist.make_icns()

        assert captured == ["/System/Library/Fonts/Apple Color Emoji.ttc"]
