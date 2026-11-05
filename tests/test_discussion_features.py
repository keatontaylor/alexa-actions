import json
from pathlib import Path

import pytest

from conftest import envelope, invoke, skill
from configuration import load_settings


def test_command_never_uses_notification_helper(fake_ha, monkeypatch):
    monkeypatch.setattr(skill, "ENABLE_COMMANDS", True)
    monkeypatch.setattr(skill, "INCLUDE_DEVICE_ID", True)
    result = invoke(
        kind="IntentRequest", intent="Command", slots={"CommandText": {"name": "CommandText", "value": "weather"}}
    )
    assert [call[0] for call in fake_ha.calls] == ["POST"]
    assert fake_ha.calls[0][1].endswith("/api/events/alexa_actionable_command")
    assert fake_ha.events[0] == {
        "command": "weather",
        "intent": "Command",
        "request_id": "test-request",
        "event_device_id": "test-device",
    }
    assert result["response"]["shouldEndSession"] is True
    invoke(kind="SessionEndedRequest", reason="USER_INITIATED", attributes=result["sessionAttributes"])
    invoke(
        kind="IntentRequest",
        intent="Command",
        slots={"CommandText": {"name": "CommandText", "value": "weather"}},
        attributes=result["sessionAttributes"],
    )
    assert len(fake_ha.events) == 1


@pytest.mark.parametrize("intent,slot", [("FreeText", "FreeTextValue"), ("String", "Strings")])
def test_legacy_standalone_string_is_opt_in(fake_ha, monkeypatch, intent, slot):
    event = envelope(kind="IntentRequest", intent=intent, slots={slot: {"name": slot, "value": "weather"}})
    event["session"]["new"] = True
    skill.lambda_handler(event, None)
    assert not fake_ha.calls
    monkeypatch.setattr(skill, "ENABLE_COMMANDS", True)
    skill.lambda_handler(event, None)
    assert fake_ha.calls[0][1].endswith("/alexa_actionable_command")
    assert "event_id" not in fake_ha.events[0]


def test_command_cannot_replace_active_question(fake_ha, monkeypatch):
    monkeypatch.setattr(skill, "ENABLE_COMMANDS", True)
    launched = invoke()
    result = invoke(
        kind="IntentRequest",
        intent="Command",
        slots={"CommandText": {"name": "CommandText", "value": "weather"}},
        attributes=launched["sessionAttributes"],
    )
    assert result["response"]["shouldEndSession"] is False
    assert not fake_ha.events


@pytest.mark.parametrize(
    "intent,key,text",
    [("AMAZON.YesIntent", "confirmation_yes", "Turning it off."), ("AMAZON.NoIntent", "confirmation_no", "")],
)
def test_custom_confirmation_uses_snapshot(fake_ha, intent, key, text):
    fake_ha.state[key] = text
    launched = invoke()
    fake_ha.state[key] = "Changed helper text"
    result = invoke(kind="IntentRequest", intent=intent, attributes=launched["sessionAttributes"])
    speech = result["response"].get("outputSpeech", {}).get("ssml", "")
    assert text in speech if text else not speech
    assert "Changed helper text" not in speech


def test_suppression_overrides_custom_confirmation(fake_ha):
    fake_ha.state.update(confirmation_yes="Custom", suppress_confirmation=True)
    launched = invoke()
    result = invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=launched["sessionAttributes"])
    assert "outputSpeech" not in result["response"]


def test_failed_post_never_speaks_custom_success(fake_ha):
    fake_ha.state["confirmation_yes"] = "Success"
    launched = invoke()
    fake_ha.post_status = 500
    result = invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=launched["sessionAttributes"])
    assert "Success" not in result["response"]["outputSpeech"]["ssml"]


def test_group_has_compact_identity_without_raw_device_id(fake_ha):
    fake_ha.state["group"] = True
    launched = invoke()
    invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=launched["sessionAttributes"])
    assert len(fake_ha.events[0]["event_device_key"]) == 16
    assert "event_device_id" not in fake_ha.events[0]


def test_settings_precedence_and_strict_booleans(tmp_path):
    defaults = dict(
        HOME_ASSISTANT_URL="https://default.invalid",
        TOKEN="",
        VERIFY_SSL=True,
        INCLUDE_DEVICE_ID=False,
        DEBUG=False,
        ENABLE_COMMANDS=False,
    )
    (tmp_path / "settings.json").write_text(
        json.dumps({"HOME_ASSISTANT_URL": "https://file.invalid/", "ENABLE_COMMANDS": True})
    )
    settings = load_settings(defaults, tmp_path, {"HOME_ASSISTANT_URL": "https://env.invalid/", "VERIFY_SSL": "false"})
    assert settings.HOME_ASSISTANT_URL == "https://env.invalid" and not settings.VERIFY_SSL and settings.ENABLE_COMMANDS
    with pytest.raises(ValueError, match="VERIFY_SSL"):
        load_settings(defaults, tmp_path, {"VERIFY_SSL": "invalid"})


def test_command_models_have_carrier_and_distinct_slot():
    for path in (Path(skill.__file__).parents[1] / "skill-package/interactionModels/custom").glob("*.json"):
        intents = json.loads(path.read_text(encoding="utf-8"))["interactionModel"]["languageModel"]["intents"]
        command = next(item for item in intents if item["name"] == "Command")
        assert command["slots"] == [{"name": "CommandText", "type": "AMAZON.SearchQuery"}]
        assert all(sample.replace("{CommandText}", "").strip() for sample in command["samples"])


def test_http_timeout_setting_is_parsed_and_bounded(tmp_path):
    defaults = dict(
        HOME_ASSISTANT_URL="https://default.invalid",
        TOKEN="",
        VERIFY_SSL=True,
        INCLUDE_DEVICE_ID=False,
        DEBUG=False,
        ENABLE_COMMANDS=False,
        HTTP_TIMEOUT=3.0,
    )
    assert load_settings(defaults, tmp_path, {}).HTTP_TIMEOUT == 3.0
    assert load_settings(defaults, tmp_path, {"HTTP_TIMEOUT": "6"}).HTTP_TIMEOUT == 6.0
    (tmp_path / "settings.json").write_text(json.dumps({"HTTP_TIMEOUT": 5}))
    assert load_settings(defaults, tmp_path, {}).HTTP_TIMEOUT == 5.0
    for bad in ("0.5", "8", "soon", True):
        with pytest.raises(ValueError, match="HTTP_TIMEOUT"):
            load_settings(defaults, tmp_path, {"HTTP_TIMEOUT": bad})


@pytest.mark.parametrize("seconds", [3.0, 6.0])
def test_http_pool_uses_the_configured_timeout(monkeypatch, seconds):
    monkeypatch.setattr(skill, "HTTP_TIMEOUT", seconds)
    timeout = skill._init_http_pool().connection_pool_kw["timeout"]
    assert timeout.total == seconds
    assert timeout.connect_timeout == pytest.approx(seconds / 3)
    assert timeout.read_timeout == pytest.approx(seconds * 2 / 3)
