"""Real HA scripts -> simulated Echo -> packaged ASK SDK -> HTTP -> real HA broker.

Only the external Alexa launch service and the HA REST authentication adapter
are simulated. State, Jinja, script queues, event bus, deadlines, SDK dispatch,
session attributes, serialization and urllib3 networking are real.
"""

import asyncio
import copy
from pathlib import Path
import tempfile

from aiohttp import ClientSession, ClientTimeout, web
from homeassistant import loader
from homeassistant.components.script.config import SCRIPT_ENTITY_SCHEMA
from homeassistant.core import Context, HomeAssistant, callback
from homeassistant.helpers import trigger
from homeassistant.helpers.config_validation import SCRIPT_SCHEMA
from homeassistant.helpers.script import Script, async_validate_actions_config
from homeassistant.util import yaml

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "simulation-only-token"


def envelope(kind="LaunchRequest", intent=None, attributes=None, device="echo-one", slots=None, reason=None):
    request = {"type": kind, "requestId": "simulation-request", "timestamp": "2026-10-10T12:00:00Z", "locale": "en-US"}
    if intent:
        request["intent"] = {"name": intent, "confirmationStatus": "NONE", "slots": slots or {}}
    if reason:
        request["reason"] = reason
    application, user = {"applicationId": "simulation-app"}, {"userId": "simulation-user"}
    return {
        "version": "1.0",
        "session": {
            "new": kind == "LaunchRequest",
            "sessionId": device,
            "application": application,
            "user": user,
            "attributes": copy.deepcopy(attributes or {}),
        },
        "context": {
            "System": {
                "application": application,
                "user": user,
                "device": {"deviceId": device, "supportedInterfaces": {}},
            }
        },
        "request": request,
    }


async def check():
    with tempfile.TemporaryDirectory() as directory:
        hass = HomeAssistant(directory)
        loader.async_setup(hass)
        await trigger.async_setup(hass)
        package = yaml.load_yaml(str(ROOT / "home-assistant/managed-notifications.yaml"))

        async def make_script(definition, name, domain="script", mode="queued", validated=False):
            actions = await async_validate_actions_config(hass, definition if validated else SCRIPT_SCHEMA(definition))
            return Script(hass, actions, name, domain, script_mode=mode, max_runs=20)

        managed = await make_script(
            SCRIPT_ENTITY_SCHEMA(package["script"]["activate_alexa_actionable_notification_managed"])["sequence"],
            "managed",
            validated=True,
        )
        broker = await make_script(package["automation"][0]["actions"], "broker", "automation")
        launcher = await make_script(
            yaml.load_yaml(str(ROOT / "home-assistant/launch-ui.yaml"))["sequence"], "launcher"
        )
        results, sessions, deliveries = [], [], []
        faults = {"get": 200, "post": 200, "malformed": False, "delay": 0}
        hass.states.async_set("counter.alexa_actionable_request", "0")
        for helper in ["notification", "pending", "completed", "group_silence"]:
            hass.states.async_set("input_text.alexa_actionable_" + helper, "")

        async def set_value(call):
            value = call.data["value"]
            assert isinstance(value, str) and len(value) <= 255
            entity = call.data["entity_id"]
            hass.states.async_set(entity[0] if isinstance(entity, list) else entity, value)

        async def increment(call):
            entity = "counter.alexa_actionable_request"
            hass.states.async_set(entity, str(int(hass.states.get(entity).state) + 1))

        @callback
        def incoming(event):
            hass.async_create_task(broker.async_run({"trigger": {"event": event}}, context=Context()))

        @callback
        def record(event):
            results.append(dict(event.data))

        hass.services.async_register("input_text", "set_value", set_value)
        hass.services.async_register("counter", "increment", increment)
        hass.bus.async_listen("alexa_actionable_notification", incoming)
        hass.bus.async_listen("alexa_actionable_notification_timeout", incoming)
        hass.bus.async_listen("alexa_actionable_notification_managed", record)

        # Real HTTP, backed by the same actual HA state and event bus as the scripts.
        async def state(request):
            assert request.headers.get("Authorization") == "Bearer " + TOKEN
            await asyncio.sleep(faults["delay"])
            if faults["get"] != 200:
                return web.Response(status=faults["get"])
            if faults["malformed"]:
                return web.Response(text="not JSON")
            return web.json_response({"state": hass.states.get(request.match_info["entity"]).state})

        async def event(request):
            assert request.headers.get("Authorization") == "Bearer " + TOKEN
            if faults["post"] != 200:
                return web.Response(status=faults["post"])
            data = await request.json()
            deliveries.append((request.match_info["event"], data))
            hass.bus.async_fire(request.match_info["event"], data)
            return web.json_response({})

        async def script_service(request):
            assert request.headers.get("Authorization") == "Bearer " + TOKEN
            data = await request.json()
            await managed.async_run(data, context=Context())
            return web.json_response([])

        app = web.Application()
        app.router.add_get("/api/states/{entity}", state)
        app.router.add_post("/api/events/{event}", event)
        app.router.add_post("/api/services/script/activate_alexa_actionable_notification_managed", script_service)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", 8765).start()
        try:
            async with ClientSession(timeout=ClientTimeout(total=10)) as http:

                async def invoke(**kwargs):
                    async with http.post("http://skill:8080/invoke", json=envelope(**kwargs)) as response:
                        assert response.status == 200
                        return await response.json()

                async def launch(call):
                    device = "echo-one" if call.domain == "media_player" else "echo-two"
                    answer = await invoke(device=device)
                    assert "E2E question" in answer["response"]["outputSpeech"]["ssml"]
                    sessions.append((device, answer["sessionAttributes"]))

                async def launch_script(call):
                    await launcher.async_run(dict(call.data), context=Context())

                hass.services.async_register("media_player", "play_media", launch)
                hass.services.async_register("alexa_devices", "send_text_command", launch)
                hass.services.async_register("script", "alexa_actionable_launch", launch_script)
                arguments = {
                    "text": "E2E question?",
                    "event_id": "same_event",
                    "alexa_device": "media_player.one",
                    "timeout_seconds": 3,
                }

                async def start(**overrides):
                    count = len(sessions)
                    task = asyncio.create_task(managed.async_run({**arguments, **overrides}, context=Context()))
                    expected = len(overrides.get("targets", [None]))
                    for _ in range(500):
                        if len(sessions) == count + expected:
                            return task, sessions[count:]
                        if task.done():
                            await task
                            raise AssertionError("Managed script completed before launching")
                        await asyncio.sleep(0.01)
                    raise AssertionError("Launch did not complete")

                async def answer(session, intent="AMAZON.YesIntent", **kwargs):
                    device, attributes = session
                    return await invoke(
                        kind="IntentRequest", intent=intent, device=device, attributes=attributes, **kwargs
                    )

                # Exercise the exported Function AND HTTP Request nodes in real Node-RED.
                count = len(sessions)
                sending = asyncio.create_task(
                    http.post(
                        "http://node-red:1880/simulate",
                        json={
                            "text": "E2E question from Node-RED?",
                            "event_id": "node_red_e2e",
                            "managed": True,
                            "timeout_seconds": 3,
                        },
                    )
                )
                for _ in range(500):
                    if len(sessions) > count:
                        break
                    await asyncio.sleep(0.01)
                assert len(sessions) == count + 1, "Node-RED did not launch the HA script"
                await answer(sessions[-1])
                response = await sending
                async with response:
                    assert response.status == 200 and await response.json() == []
                await hass.async_block_till_done()
                assert results[-1]["event_id"] == "node_red_e2e"

                for intent, expected in [
                    ("AMAZON.YesIntent", "ResponseYes"),
                    ("AMAZON.NoIntent", "ResponseNo"),
                    ("Number", "ResponseNumeric"),
                    ("String", "ResponseString"),
                ]:
                    task, current = await start(confirmation_yes="Done", confirmation_no="Declined")
                    slots = {}
                    if intent in {"Number", "String"}:
                        name = "Numbers" if intent == "Number" else "Strings"
                        slots = {name: {"name": name, "value": "42", "confirmationStatus": "NONE"}}
                    reply = await answer(current[0], intent, slots=slots)
                    await task
                    await hass.async_block_till_done()
                    assert results[-1]["event_response_type"] == expected
                    assert results[-1]["request_id"] == current[0][1]["alexa_actionable_notification"]["request_id"]
                    if intent in {"AMAZON.YesIntent", "AMAZON.NoIntent"}:
                        assert ("Done" if intent == "AMAZON.YesIntent" else "Declined") in reply["response"][
                            "outputSpeech"
                        ]["ssml"]

                # A changed helper and delayed callback cannot resolve the next question.
                old = current[0]
                count = len(results)
                task, current = await start(suppress_confirmation=True)
                await invoke(kind="SessionEndedRequest", attributes=old[1], reason="EXCEEDED_MAX_REPROMPTS")
                await asyncio.sleep(0.02)
                assert len(results) == count
                reply = await answer(current[0])
                await task
                assert "outputSpeech" not in reply["response"]
                await answer(current[0])  # Replay original attributes; HA broker must deduplicate.
                await hass.async_block_till_done()
                assert len(results) == count + 1

                task, current = await start(timeout_seconds=0.1)
                await task
                await hass.async_block_till_done()
                assert results[-1]["event_response_type"] == "ResponseNone"
                count = len(results)
                await answer(current[0])
                await hass.async_block_till_done()
                assert len(results) == count

                targets = [{"alexa_device": "media_player.one"}, {"transport": "alexa_devices", "device_id": "ha-two"}]
                task, current = await start(targets=targets)
                await invoke(
                    kind="SessionEndedRequest", device=current[0][0], attributes=current[0][1], reason="USER_INITIATED"
                )
                await invoke(
                    kind="SessionEndedRequest", device=current[0][0], attributes=current[0][1], reason="USER_INITIATED"
                )
                await asyncio.sleep(0.02)
                assert len(results) == count
                await answer(current[1], "AMAZON.NoIntent")
                await task
                await answer(current[0])
                await hass.async_block_till_done()
                assert len(results) == count + 1 and results[-1]["event_response_type"] == "ResponseNo"

                task, current = await start(targets=targets)
                for device, attributes in current:
                    await invoke(
                        kind="SessionEndedRequest", device=device, attributes=attributes, reason="USER_INITIATED"
                    )
                await task
                await hass.async_block_till_done()
                assert results[-1]["event_response_type"] == "ResponseNone"

                # Failed deliveries do not mark the session completed; deadline still resolves it.
                task, current = await start(timeout_seconds=0.15)
                faults["post"] = 503
                reply = await answer(current[0])
                assert "503" in reply["response"]["outputSpeech"]["ssml"]
                assert not reply["sessionAttributes"]["alexa_actionable_notification_completed"]
                await task
                faults["post"] = 200
                assert results[-1]["event_response_type"] == "ResponseNone"

                for status in [401, 404, 500]:
                    faults["get"] = status
                    reply = await invoke()
                    assert str(status) in reply["response"]["outputSpeech"]["ssml"]
                faults["get"] = 200
                faults["malformed"] = True
                reply = await invoke()
                assert "alexa_actionable_notification" not in reply["sessionAttributes"]
                faults["malformed"] = False
                faults["delay"] = 2.5  # Exceeds the actual urllib3 read deadline.
                before = asyncio.get_running_loop().time()
                reply = await invoke()
                assert asyncio.get_running_loop().time() - before < 4
                assert "alexa_actionable_notification" not in reply["sessionAttributes"]
                faults["delay"] = 0
                reply = await invoke(
                    kind="IntentRequest",
                    intent="Command",
                    slots={"CommandText": {"name": "CommandText", "value": "turn lights on"}},
                )
                assert reply["response"]["shouldEndSession"]
                assert deliveries[-1][0] == "alexa_actionable_command"
                assert deliveries[-1][1]["command"] == "turn lights on"
                print(
                    "E2E PASS: Node-RED runtime, packaged SDK, real HTTP/auth, HA scripts/broker, replies, stale/duplicate callbacks, groups, deadlines, faults, commands",
                    flush=True,
                )
        finally:
            await runner.cleanup()
            await hass.async_stop(force=True)


if __name__ == "__main__":
    asyncio.run(check())
