"""JSON configuration persistence, independent of Qt and its views."""
import json
from pathlib import Path
import shutil


class ConfigStore:
    def __init__(self, config_path: Path, default_path: Path):
        self.config_path = Path(config_path)
        self.default_path = Path(default_path)

    def load(self) -> dict:
        if not self.config_path.exists():
            shutil.copy(self.default_path, self.config_path)
        with self.config_path.open(encoding="utf-8") as stream:
            return json.load(stream)

    def save(self, config: dict) -> None:
        with self.config_path.open("w", encoding="utf-8") as stream:
            json.dump(config, stream, indent=2, ensure_ascii=False)
