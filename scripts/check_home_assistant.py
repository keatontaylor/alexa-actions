"""Run inside the official HA container; fake only outgoing launch actions."""

import asyncio
import json
import logging
from pathlib import Path
import tempfile

from homeassistant import loader
from homeassistant.components.automation import config as automation_config
from homeassistant.components.blueprint.models import Blueprint
from homeassistant.components.blueprint.schemas import BLUEPRINT_SCHEMA
from homeassistant.components.script.config import SCRIPT_ENTITY_SCHEMA
from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import trigger
from homeassistant.helpers.script import Script, async_validate_actions_config
from homeassistant.helpers.template import Template
from homeassistant.util import yaml

ROOT = Path(__file__).resolve().parents[1]


async def check():
    with tempfile.TemporaryDirectory() as directory:
        hass = HomeAssistant(directory)
        loader.async_setup(hass)
        await trigger.async_setup(hass)
        config = yaml.load_yaml(str(ROOT / "home-assistant/configuration.yaml"))
        ui = yaml.load_yaml(str(ROOT / "home-assistant/script-ui.yaml"))
        assert config["script"]["activate_alexa_actionable_notification"] == ui
        definition = SCRIPT_ENTITY_SCHEMA(ui)
        sequence = await async_validate_actions_config(hass, definition["sequence"])
        calls = []

        async def capture(call):
            calls.append((call.domain, call.service, dict(call.data)))
            if call.domain == "input_text":
                value = call.data["value"]
                assert isinstance(value, str), type(value)
                assert len(value) <= 255
                json.loads(value)

        hass.services.async_register("input_text", "set_value", capture)
        hass.services.async_register("media_player", "play_media", capture)
        hass.services.async_register("alexa_devices", "send_text_command", capture)
        script = Script(hass, sequence, "example test", "script")
        # Exercise escaping, defaults, alias precedence and both transport branches.
        for parameters in [
            {
                "text": 'Quotes " and slash \\ and newline\n ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©',
                "event_id": "qa",
                "alexa_device": "media_player.test",
            },
            {"message": "Legacy question", "event_id": "qb", "alexa_device": "media_player.test"},
            {"text": "Preferred", "message": "Ignored", "event_id": "qc", "alexa_device": "media_player.test"},
            {
                "text": "Native?",
                "event_id": "qd",
                "transport": "alexa_devices",
                "device_id": "ha-device",
                "invocation_name": "test notifications",
                "suppress_confirmation": True,
            },
        ]:
            calls.clear()
            await script.async_run(parameters, context=Context())
            assert len(calls) == 2, calls
            stored = json.loads(calls[0][2]["value"])
            assert stored["text"] == parameters.get("text", parameters.get("message"))
            assert stored["event"] == parameters["event_id"]
            assert stored["suppress_confirmation"] is parameters.get("suppress_confirmation", False)
            if parameters.get("transport") == "alexa_devices":
                assert calls[1] == (
                    "alexa_devices",
                    "send_text_command",
                    {"device_id": "ha-device", "text_command": "open test notifications"},
                )
            else:
                assert calls[1][2]["media_content_type"] == "skill"
        for parameters in [{"text": "x" * 256, "event_id": "too-long"}, {"event_id": "missing-text"}]:
            calls.clear()
            try:
                await script.async_run(parameters, context=Context())
            except HomeAssistantError:
                pass
            assert calls == []

        blueprint_data = yaml.load_yaml(str(ROOT / "home-assistant/alexa_actions_skill_automation_template.yaml"))
        blueprint = Blueprint(blueprint_data, expected_domain="automation", schema=BLUEPRINT_SCHEMA)
        inputs = {name: item["default"] for name, item in blueprint.inputs.items() if "default" in item}
        inputs.update(AlexaResponceTrigger="input_boolean.test", AlexaNotifier="media_player.test")
        expanded = yaml.substitute(blueprint_data, inputs)
        expanded.pop("blueprint")
        assert await automation_config.async_validate_config_item(hass, "test", expanded) is not None
        for condition in expanded["conditions"][1:]:
            condition_template = Template(str(condition["value_template"]), hass)
            assert condition_template.async_render(variables=expanded["variables"]) is True
        confirmation = expanded["actions"][0]["choose"][0]["sequence"][0]["data"]["suppress_confirmation"]
        confirmation = Template(str(confirmation), hass)
        assert confirmation.async_render(variables={"allow_confirmation": True}) is False
        assert confirmation.async_render(variables={"allow_confirmation": False}) is True
        for example in yaml.load_yaml(str(ROOT / "home-assistant/event-example.yaml")):
            assert await automation_config.async_validate_config_item(hass, "example", example) is not None
        print("HA script execution, blueprint defaults, confirmation flags and event example OK")
        await hass.async_stop(force=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(check())
