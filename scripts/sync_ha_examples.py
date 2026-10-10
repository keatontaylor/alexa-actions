"""Regenerate file-based script wrappers from the canonical UI definitions."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1] / "home-assistant"


def sync():
    path = ROOT / "configuration.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    for script_id, filename in (
        ("activate_alexa_actionable_notification", "script-ui.yaml"),
        ("alexa_actionable_launch", "launch-ui.yaml"),
    ):
        config["script"][script_id] = yaml.safe_load((ROOT / filename).read_text(encoding="utf-8"))
    path.write_bytes(yaml.safe_dump(config, sort_keys=False, allow_unicode=True, width=120).encode("utf-8"))


if __name__ == "__main__":
    sync()
