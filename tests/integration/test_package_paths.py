"""Package/resource discovery must not depend on the launch directory."""
import json
import os
from pathlib import Path
import subprocess
import sys

from purr_pause.infrastructure.paths import resource_path, user_data_dir


ROOT = Path(__file__).resolve().parents[2]


def test_source_resources_and_config_location_from_another_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    assert user_data_dir() == ROOT
    assert resource_path("config/config.default.json").is_file()
    assert resource_path("assets/fonts/NotoSansSC[wght].ttf").is_file()
    manifest = json.loads(resource_path("assets/cat_anim/manifest.json").read_text())
    assert len(manifest["frames"]) == 611
    assert all(resource_path(f"assets/cat_anim/frame_{i:03d}.png").is_file()
               for i in range(1, 612))


def test_version_import_has_no_qt_or_configuration_side_effects(tmp_path):
    env = dict(os.environ, PYTHONPATH=str(ROOT), APPDATA=str(tmp_path))
    result = subprocess.run([
        sys.executable, "-c",
        "import sys; from purr_pause.version import VERSION; "
        "assert not any(k.startswith('PyQt6') for k in sys.modules); print(VERSION)",
    ], cwd=tmp_path, env=env, capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "0.1.2"
    assert not list(tmp_path.iterdir())


def test_frozen_default_location_matches_build_destination(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path("config/config.default.json") == tmp_path / "config" / "config.default.json"
