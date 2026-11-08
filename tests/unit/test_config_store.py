import json

import pytest

from purr_pause.infrastructure.config_store import ConfigStore


def test_first_load_copies_default_bytes(tmp_path):
    default = tmp_path / "default.json"
    raw = b'{\n "interval_minutes": 20, "cat_image_path": ""\n}\n'
    default.write_bytes(raw)
    target = tmp_path / "config.json"

    assert ConfigStore(target, default).load()["interval_minutes"] == 20
    assert target.read_bytes() == raw


def test_existing_config_preserves_unknown_and_missing_optional_fields(tmp_path):
    target = tmp_path / "config.json"
    existing = {"interval_minutes": 2, "future_setting": {"enabled": True}}
    raw = json.dumps(existing).encode()
    target.write_bytes(raw)

    assert ConfigStore(target, tmp_path / "missing-default.json").load() == existing
    assert target.read_bytes() == raw


def test_save_uses_existing_json_format(tmp_path):
    target = tmp_path / "config.json"
    config = {"interval_minutes": 2, "cat_image_path": "猫.png"}

    ConfigStore(target, tmp_path / "default.json").save(config)

    assert target.read_text(encoding="utf-8") == json.dumps(config, indent=2, ensure_ascii=False)


def test_invalid_existing_json_propagates_without_overwriting(tmp_path):
    target = tmp_path / "config.json"
    target.write_bytes(b"{bad json")

    with pytest.raises(json.JSONDecodeError):
        ConfigStore(target, tmp_path / "default.json").load()

    assert target.read_bytes() == b"{bad json"
