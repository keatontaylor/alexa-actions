import json
from unittest.mock import Mock

import pytest
import urllib3

from conftest import envelope, invoke, skill


def session():
    return invoke()["sessionAttributes"]


def slot(name, value):
    return {name: {"name": name, "value": value, "confirmationStatus": "NONE"}}


def test_old_answer_keeps_original_event(fake_ha):
    attributes = session()
    fake_ha.state["event"] = "new_question"
    invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=attributes)
    assert fake_ha.events[0]["event_id"] == "test_a"
    assert [method for method, *_ in fake_ha.calls] == ["GET", "POST"]


def test_interleaved_launches_have_independent_context(fake_ha):
    first = session()
    fake_ha.state.update(event="test_b", text="Second question?")
    second = session()
    invoke(kind="IntentRequest", intent="AMAZON.NoIntent", attributes=first)
    invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=second)
    assert [event["event_id"] for event in fake_ha.events] == ["test_a", "test_b"]


@pytest.mark.parametrize(
    "intent,slots,response_type,response",
    [
        ("AMAZON.YesIntent", {}, "ResponseYes", "ResponseYes"),
        ("AMAZON.NoIntent", {}, "ResponseNo", "ResponseNo"),
        ("Number", slot("Numbers", "42"), "ResponseNumeric", "42"),
        ("String", slot("Strings", "test value"), "ResponseString", "test value"),
        ("Duration", slot("Durations", "PT5M"), "ResponseDuration", 300),
        ("Date", slot("Dates", "2026-09-26"), "ResponseDateTime", None),
        ("AMAZON.FallbackIntent", {}, "ResponseNone", "ResponseNone"),
        ("AMAZON.StopIntent", {}, "ResponseNone", "ResponseNone"),
        ("AMAZON.CancelIntent", {}, "ResponseNone", "ResponseNone"),
    ],
)
@pytest.mark.parametrize("suppressed", [True, False])
def test_terminal_responses_and_suppression(fake_ha, intent, slots, response_type, response, suppressed):
    fake_ha.state["suppress_confirmation"] = suppressed
    result = invoke(kind="IntentRequest", intent=intent, slots=slots, attributes=session())
    event = fake_ha.events[0]
    assert event["event_response_type"] == response_type
    if response is not None:
        assert event["event_response"] == response
    else:
        assert json.loads(event["event_response"])["year"] == "2026"
    assert result["response"]["shouldEndSession"] is True
    if suppressed and intent not in {"AMAZON.StopIntent", "AMAZON.CancelIntent"}:
        assert "outputSpeech" not in result["response"]
    completed = result["sessionAttributes"]
    invoke(kind="SessionEndedRequest", reason="USER_INITIATED", attributes=completed)
    invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=completed)
    assert len(fake_ha.events) == 1


def selection_slots():
    return {
        "Selections": {
            "name": "Selections",
            "value": "kitchen",
            "resolutions": {
                "resolutionsPerAuthority": [
                    {
                        "authority": "test",
                        "status": {"code": "ER_SUCCESS_MATCH"},
                        "values": [{"value": {"name": "Kitchen", "id": "kitchen"}}],
                    }
                ]
            },
        }
    }


@pytest.mark.parametrize("status,suppressed", [(200, False), (200, True), (401, False), (500, False)])
def test_selection_preserves_errors_and_suppression(fake_ha, status, suppressed):
    fake_ha.state["suppress_confirmation"] = suppressed
    attributes = session()
    fake_ha.post_status = status
    result = invoke(kind="IntentRequest", intent="Select", slots=selection_slots(), attributes=attributes)
    assert result["response"]["shouldEndSession"] is True
    speech = result["response"].get("outputSpeech", {}).get("ssml", "")
    if status != 200:
        assert str(status) in speech and "Kitchen" not in speech
        assert not result["sessionAttributes"][skill.COMPLETED_KEY]
    elif suppressed:
        assert not speech
    else:
        assert "Kitchen" in speech


@pytest.mark.parametrize("status", [401, 404, 500, 302])
def test_launch_http_errors_are_terminal(fake_ha, status):
    fake_ha.get_status = status
    result = invoke()
    assert str(status) in result["response"]["outputSpeech"]["ssml"]
    assert result["response"]["shouldEndSession"] is True
    assert len(fake_ha.calls) == 1 and fake_ha.events == []


@pytest.mark.parametrize(
    "raw",
    [
        "not JSON",
        "null",
        "[]",
        "{}",
        '{"state":"unknown"}',
        '{"state":"unavailable"}',
        '{"state":"[]"}',
        '{"state":"{}"}',
        '{"state":"{"text": 42}"}',
    ],
)
def test_invalid_helper_does_not_rethrow_or_refetch(fake_ha, raw):
    fake_ha.raw_state = raw
    result = invoke()
    assert result["response"]["shouldEndSession"] is True
    assert len(fake_ha.calls) == 1 and fake_ha.events == []


def test_missing_token_stops_before_http(fake_ha, monkeypatch):
    monkeypatch.setattr(skill, "TOKEN", "")
    result = invoke()
    assert result["response"]["shouldEndSession"] is True
    assert not fake_ha.calls


def test_network_timeout_does_not_recurse(fake_ha):
    fake_ha.error = urllib3.exceptions.ReadTimeoutError(None, "/test", "timeout")
    result = invoke()
    assert result["response"]["shouldEndSession"] is True
    assert len(fake_ha.calls) == 1


@pytest.mark.parametrize("intent", ["Number", "Select", "String", "Duration", "Date"])
def test_missing_slots_reprompt_original_question(fake_ha, intent):
    attributes = session()
    fake_ha.state["text"] = "Do not repeat this replacement"
    result = invoke(kind="IntentRequest", intent=intent, attributes=attributes)
    assert result["response"]["shouldEndSession"] is False
    assert "Test question?" in result["response"]["outputSpeech"]["ssml"]
    assert len(fake_ha.calls) == 1 and fake_ha.events == []


def test_no_session_never_posts_current_helper(fake_ha):
    result = invoke(kind="IntentRequest", intent="AMAZON.YesIntent")
    assert result["response"]["shouldEndSession"] is True
    result = invoke(kind="SessionEndedRequest", reason="EXCEEDED_MAX_REPROMPTS")
    assert "outputSpeech" not in result["response"]
    assert not fake_ha.calls


def test_end_callback_keeps_original_event_and_is_silent(fake_ha):
    attributes = session()
    fake_ha.state["event"] = "replacement"
    result = invoke(kind="SessionEndedRequest", reason="EXCEEDED_MAX_REPROMPTS", attributes=attributes)
    assert fake_ha.events[0]["event_id"] == "test_a"
    assert fake_ha.events[0]["event_response_type"] == "ResponseNone"
    assert "outputSpeech" not in result["response"]


def test_person_and_device_metadata_are_optional(fake_ha, monkeypatch):
    attributes = session()
    event = envelope(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=attributes)
    event["context"]["System"]["person"] = {"personId": "recognized-person"}
    monkeypatch.setattr(skill, "INCLUDE_DEVICE_ID", True)
    skill.lambda_handler(event, None)
    assert fake_ha.events[0]["event_person_id"] == "recognized-person"
    assert fake_ha.events[0]["event_device_id"] == "test-device"


def test_default_omits_device_and_person(fake_ha):
    invoke(kind="IntentRequest", intent="AMAZON.NoIntent", attributes=session())
    assert "event_person_id" not in fake_ha.events[0] and "event_device_id" not in fake_ha.events[0]


def test_managed_request_id_is_preserved(fake_ha):
    fake_ha.state["request_id"] = "unique-invocation"
    invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=session())
    assert fake_ha.events[0]["request_id"] == "unique-invocation"


def test_extra_headers_preserve_authorization(fake_ha):
    handler = Mock()
    handler.attributes_manager.request_attributes = {
        "_": json.loads((skill.Path(skill.__file__).parent / "language_strings.json").read_text())["en"]
    }
    handler.attributes_manager.session_attributes = {}
    # No launch means this construction cannot fetch the global helper.
    monkey_request = Mock()
    handler.request_envelope.request = monkey_request
    monkey_request.object_type = "IntentRequest"
    client = skill.HomeAssistant(handler)
    client._get("api", "test", extra_headers={"X-Test": "present"})
    client._post("api", "test", body={}, extra_headers={"X-Test": "present"})
    for _, _, headers, _ in fake_ha.calls:
        assert headers["Authorization"] == "Bearer test-only-token"
        assert headers["X-Test"] == "present"


def test_current_simple_slot_value_shape(fake_ha):
    attributes = session()
    slots = {"Numbers": {"name": "Numbers", "slotValue": {"type": "Simple", "value": "17"}}}
    invoke(kind="IntentRequest", intent="Number", slots=slots, attributes=attributes)
    assert fake_ha.events[0]["event_response"] == "17"


def test_post_timeout_does_not_mark_delivered(fake_ha):
    attributes = session()
    fake_ha.error = urllib3.exceptions.ReadTimeoutError(None, "/event", "timeout")
    result = invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=attributes)
    assert result["sessionAttributes"][skill.COMPLETED_KEY] is False
    assert result["response"]["shouldEndSession"] is True
    assert len(fake_ha.calls) == 2
