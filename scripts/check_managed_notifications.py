"""Exercise managed deadlines and the broker with the real HA script engine."""

import asyncio
import json
from pathlib import Path
import tempfile

from homeassistant import loader
from homeassistant.components.automation import config as automation_config
from homeassistant.components.script.config import SCRIPT_ENTITY_SCHEMA
from homeassistant.core import Context, HomeAssistant, callback
from homeassistant.helpers import trigger
from homeassistant.helpers.config_validation import SCRIPT_SCHEMA
from homeassistant.helpers.script import Script, async_validate_actions_config
from homeassistant.util import yaml

ROOT = Path(__file__).resolve().parents[1]


async def check():
    with tempfile.TemporaryDirectory() as directory:
        hass = HomeAssistant(directory)
        loader.async_setup(hass)
        await trigger.async_setup(hass)
        package = yaml.load_yaml(str(ROOT / "home-assistant/managed-notifications.yaml"))
        definition = SCRIPT_ENTITY_SCHEMA(package["script"]["activate_alexa_actionable_notification_managed"])
        sequence = await async_validate_actions_config(hass, definition["sequence"])
        broker_definition = package["automation"][0]
        assert await automation_config.async_validate_config_item(hass, "broker", broker_definition) is not None
        broker_sequence = await async_validate_actions_config(hass, SCRIPT_SCHEMA(broker_definition["actions"]))
        managed = Script(hass, sequence, "managed test", "script", script_mode="queued")
        broker = Script(hass, broker_sequence, "broker test", "automation", script_mode="queued", max_runs=50)
        results = []
        launched = []
        immediate = True
        response_value = None
        tasks = []
        hass.states.async_set("counter.alexa_actionable_request", "0")
        for helper in ["alexa_actionable_pending", "alexa_actionable_completed"]:
            hass.states.async_set("input_text." + helper, "")

        async def set_value(call):
            assert isinstance(call.data["value"], str)
            assert len(call.data["value"]) <= 255
            entity = call.data["entity_id"]
            entity = entity[0] if isinstance(entity, list) else entity
            hass.states.async_set(entity, call.data["value"])

        async def increment(call):
            value = int(hass.states.get("counter.alexa_actionable_request").state)
            hass.states.async_set("counter.alexa_actionable_request", str(value + 1))

        async def launch(call):
            question = json.loads(hass.states.get("input_text.alexa_actionable_notification").state)
            launched.append(question)
            if immediate:
                event_data = response(question)
                if response_value is not None:
                    event_data.update(event_response=response_value, event_response_type="ResponseString")
                hass.bus.async_fire("alexa_actionable_notification", event_data)
                # Complete during the launch action, before the managed script begins waiting.
                await asyncio.sleep(0.01)

        def response(question, response_type="ResponseYes"):
            return {
                "event_id": question["event"],
                "request_id": question["request_id"],
                "event_response": response_type,
                "event_response_type": response_type,
                "event_person_id": "test-person",
                "event_device_id": "test-device",
            }

        @callback
        def incoming(event):
            tasks.append(hass.async_create_task(broker.async_run({"trigger": {"event": event}}, context=Context())))

        hass.services.async_register("input_text", "set_value", set_value)
        hass.services.async_register("counter", "increment", increment)
        hass.services.async_register("media_player", "play_media", launch)
        hass.services.async_register("alexa_devices", "send_text_command", launch)
        hass.bus.async_listen("alexa_actionable_notification", incoming)
        hass.bus.async_listen("alexa_actionable_notification_timeout", incoming)

        @callback
        def record(event):
            results.append(dict(event.data))

        hass.bus.async_listen("alexa_actionable_notification_managed", record)
        arguments = {
            "text": "Managed question?",
            "event_id": "reused_event",
            "alexa_device": "media_player.test",
            "timeout_seconds": 0.05,
        }
        await managed.async_run(arguments, context=Context())
        await hass.async_block_till_done()
        assert len(results) == 1 and results[0]["event_response_type"] == "ResponseYes", results
        assert results[0]["event_person_id"] == "test-person"
        first_question = launched[-1]
        hass.bus.async_fire("alexa_actionable_notification", response(first_question))
        await hass.async_block_till_done()
        assert len(results) == 1

        immediate = False
        await managed.async_run(arguments, context=Context())
        await hass.async_block_till_done()
        assert len(results) == 2 and results[-1]["event_response_type"] == "ResponseNone", results
        timed_out = launched[-1]
        hass.bus.async_fire("alexa_actionable_notification", response(timed_out))
        await hass.async_block_till_done()
        assert len(results) == 2

        # Queue two overlapping calls, reject a previous session's reply during the next call.
        arguments["timeout_seconds"] = 1
        before = len(launched)
        shared_context = Context()
        first = asyncio.create_task(managed.async_run(arguments, context=shared_context))
        second = asyncio.create_task(managed.async_run(arguments, context=shared_context))
        for _ in range(100):
            if len(launched) > before:
                break
            await asyncio.sleep(0.001)
        assert len(launched) == before + 1
        current = launched[-1]
        hass.bus.async_fire("alexa_actionable_notification", response(timed_out))
        await asyncio.sleep(0.01)
        assert len(results) == 2
        hass.bus.async_fire("alexa_actionable_notification", response(current, "ResponseNo"))
        await first
        for _ in range(100):
            if len(launched) > before + 1:
                break
            await asyncio.sleep(0.001)
        assert len(launched) == before + 2
        next_question = launched[-1]
        assert next_question["request_id"] != current["request_id"]
        hass.bus.async_fire("alexa_actionable_notification", response(current))
        hass.bus.async_fire("alexa_actionable_notification", response(next_question))
        hass.bus.async_fire("alexa_actionable_notification_timeout", response(next_question, "ResponseNone"))
        await second
        await hass.async_block_till_done()
        assert len(results) == 4, results
        assert [item["event_response_type"] for item in results] == [
            "ResponseYes",
            "ResponseNone",
            "ResponseNo",
            "ResponseYes",
        ], results
        assert len({item["request_id"] for item in results}) == 4
        assert all(item["event_id"] == "reused_event" for item in results)
        immediate = True
        for response_value in ["42", "null", '{"year":"2026"}', 300.5]:
            await managed.async_run(arguments, context=Context())
            await hass.async_block_till_done()
            assert results[-1]["raw_event"]["event_response"] == response_value
            assert type(results[-1]["raw_event"]["event_response"]) is type(response_value)
        print("HA managed immediate replies, timeout, duplicates, stale sessions and queued overlap OK")
        await hass.async_stop(force=True)


if __name__ == "__main__":
    asyncio.run(check())
