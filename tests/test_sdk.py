from conftest import invoke


def test_real_sdk_launch_and_yes(fake_ha):
    launched = invoke()
    assert "Test question?" in launched["response"]["outputSpeech"]["ssml"]
    assert launched["response"]["shouldEndSession"] is False
    invoke(kind="IntentRequest", intent="AMAZON.YesIntent", attributes=launched.get("sessionAttributes"))
    assert fake_ha.events[0]["event_id"] == "test_a"
    assert fake_ha.events[0]["event_response_type"] == "ResponseYes"


def test_all_current_models_are_parseable():
    import json
    from pathlib import Path

    for path in (Path(__file__).resolve().parents[1] / "skill-package/interactionModels/custom").glob("*.json"):
        model = json.loads(path.read_text(encoding="utf-8"))
        intents = model["interactionModel"]["languageModel"]["intents"]
        assert {"AMAZON.YesIntent", "AMAZON.NoIntent"} <= {item["name"] for item in intents}
