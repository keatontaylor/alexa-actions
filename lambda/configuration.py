"""Settings precedence: deployed constants < private JSON file < environment."""

from dataclasses import dataclass
import json
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    HOME_ASSISTANT_URL: str
    TOKEN: str = ""
    VERIFY_SSL: bool = True
    INCLUDE_DEVICE_ID: bool = False
    DEBUG: bool = False
    ENABLE_COMMANDS: bool = False


def load_settings(defaults, directory, environ=None):
    environ = os.environ if environ is None else environ
    values = dict(defaults)
    configured = environ.get("ALEXA_ACTIONS_CONFIG")
    path = Path(configured) if configured else Path(directory) / "settings.json"
    if configured or path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or set(data) - set(Settings.__dataclass_fields__):
            raise ValueError("Settings file must contain only supported configuration keys")
        values.update(data)
    values.update({key: environ[key] for key in Settings.__dataclass_fields__ if key in environ})
    for key in ("VERIFY_SSL", "INCLUDE_DEVICE_ID", "DEBUG", "ENABLE_COMMANDS"):
        value = values[key]
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            value = value.lower() == "true"
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be true or false")
        values[key] = value
    for key in ("HOME_ASSISTANT_URL", "TOKEN"):
        if not isinstance(values[key], str):
            raise ValueError(f"{key} must be a string")
    values["HOME_ASSISTANT_URL"] = values["HOME_ASSISTANT_URL"].rstrip("/")
    return Settings(**values)
