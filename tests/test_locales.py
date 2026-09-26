import json
from pathlib import Path
import re
from unittest.mock import Mock

import pytest

from conftest import invoke, skill

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "skill-package/interactionModels/custom"
LOCALES = sorted(path.stem for path in MODELS.glob("*.json"))


def test_models_and_manifest_match():
    manifest = json.loads((ROOT / "skill-package/skill.json").read_text())
    assert set(LOCALES) == set(manifest["manifest"]["publishingInformation"]["locales"])
    assert {"en-CA", "en-IN", "es-US"} <= set(LOCALES)


@pytest.mark.parametrize("locale", LOCALES)
def test_models_have_handler_slot_contracts_and_valid_phrase_samples(locale):
    model = json.loads((MODELS / (locale + ".json")).read_text(encoding="utf-8"))
    intents = model["interactionModel"]["languageModel"]["intents"]
    names = [intent["name"] for intent in intents]
    assert len(names) == len(set(names))
    assert {"AMAZON.YesIntent", "AMAZON.NoIntent", "AMAZON.FallbackIntent", "AMAZON.HelpIntent"} <= set(names)
    expected = {
        "String": ("Strings", None),
        "FreeText": ("FreeText", "AMAZON.SearchQuery"),
        "Number": ("Numbers", "AMAZON.NUMBER"),
        "Duration": ("Durations", "AMAZON.DURATION"),
        "Select": ("Selections", "Selections"),
    }
    for intent in intents:
        declared = {slot["name"] for slot in intent.get("slots", [])}
        for sample in intent.get("samples", []):
            assert set(re.findall(r"{([^}]+)}", sample)) <= declared
        if intent["name"] in expected:
            slot_name, slot_type = expected[intent["name"]]
            assert declared == {slot_name}
            if slot_type:
                assert intent["slots"][0]["type"] == slot_type
        if intent["name"] == "FreeText":
            assert all(sample.replace("{FreeText}", "").strip() for sample in intent["samples"])
            assert all(sample.count("{FreeText}") == 1 for sample in intent["samples"])


@pytest.mark.parametrize("locale", LOCALES)
@pytest.mark.parametrize("intent", ["AMAZON.YesIntent", "AMAZON.NoIntent", "FreeText", "AMAZON.HelpIntent"])
def test_regional_sdk_dispatch(fake_ha, locale, intent):
    launched = invoke(locale=locale)
    slots = {"FreeText": {"name": "FreeText", "value": "leave the kitchen lights on"}} if intent == "FreeText" else {}
    result = invoke(
        kind="IntentRequest", intent=intent, slots=slots, locale=locale, attributes=launched["sessionAttributes"]
    )
    speech = result["response"].get("outputSpeech", {}).get("ssml", "")
    assert "You just triggered" not in speech
    if intent == "AMAZON.HelpIntent":
        assert "Test question?" in speech
        assert result["response"]["shouldEndSession"] is False
        assert not fake_ha.events
    else:
        expected = {"AMAZON.YesIntent": "ResponseYes", "AMAZON.NoIntent": "ResponseNo", "FreeText": "ResponseString"}
        assert fake_ha.events[0]["event_response_type"] == expected[intent]
        if intent == "FreeText":
            assert fake_ha.events[0]["event_response"] == "leave the kitchen lights on"
        assert result["response"]["shouldEndSession"] is True
    assert len([call for call in fake_ha.calls if call[0] == "GET"]) == 1


@pytest.mark.parametrize("locale", ["xx-XX", None, "fr-FR", "fr-CA"])
def test_localization_fallback_and_french_override(locale):
    handler = Mock()
    handler.request_envelope.request.locale = locale
    handler.attributes_manager.request_attributes = {}
    skill.LocalizationInterceptor().process(handler)
    prompts = handler.attributes_manager.request_attributes["_"]
    assert prompts["ERROR_CONFIG"]
    if locale in {"fr-FR", "fr-CA"}:
        assert prompts["SKILL_NAME"] == "Actionable notifications"
    else:
        assert prompts["OKAY"] == "Okay"


def test_unknown_locale_safe_sdk_response(fake_ha):
    result = invoke(locale="xx-XX")
    assert "Test question?" in result["response"]["outputSpeech"]["ssml"]


def test_navigate_home_completes_pending_question(fake_ha):
    launched = invoke()
    result = invoke(kind="IntentRequest", intent="AMAZON.NavigateHomeIntent", attributes=launched["sessionAttributes"])
    assert result["response"]["shouldEndSession"] is True
    assert fake_ha.events[0]["event_response_type"] == "ResponseNone"


def test_translations_keep_original_unicode():
    strings = json.loads((ROOT / "lambda/language_strings.json").read_text(encoding="utf-8"))
    assert "você" in strings["pt"]["ERROR_404"]
    assert "l'entité" in strings["fr"]["ERROR_404"]
    for path in MODELS.glob("*.json"):
        content = path.read_text(encoding="utf-8")
        assert not re.search(r"[\u00c2\u00c3][\u0080-\u00bf]", content)
