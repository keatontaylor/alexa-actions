"""Real ASK SDK dispatch with a fake HA HTTP boundary, never an Amazon/HA account."""

import copy
import json
from pathlib import Path
import sys

import pytest
from urllib3 import HTTPResponse

LAMBDA = Path(__file__).resolve().parents[1] / "lambda"
sys.path.insert(0, str(LAMBDA))
import lambda_function as skill  # noqa: E402


class FakeHA:
    def __init__(self):
        self.state = {"text": "Test question?", "event": "test_a", "suppress_confirmation": False}
        self.calls = []
        self.events = []
        self.get_status = 200
        self.post_status = 200
        self.raw_state = None
        self.error = None

    def request(self, method, url, headers=None, body=None, **kwargs):
        self.calls.append((method, url, headers, body))
        if self.error:
            raise self.error
        if method == "GET":
            data = self.raw_state if self.raw_state is not None else json.dumps({"state": json.dumps(self.state)})
            return HTTPResponse(status=self.get_status, body=data.encode())
        event = json.loads(body)
        if self.post_status < 400:
            self.events.append(event)
        return HTTPResponse(status=self.post_status, body=b"{}")


@pytest.fixture
def fake_ha(monkeypatch):
    fake = FakeHA()
    monkeypatch.setattr(skill, "_init_http_pool", lambda: fake)
    monkeypatch.setattr(skill, "TOKEN", "test-only-token")
    monkeypatch.chdir(LAMBDA)
    if hasattr(skill, "Borg"):
        skill.Borg._shared_state.clear()
    return fake


def envelope(kind="LaunchRequest", intent=None, attributes=None, slots=None, locale="en-US", reason=None):
    request = {"type": kind, "requestId": "test-request", "timestamp": "2026-09-26T12:00:00Z", "locale": locale}
    if intent:
        request["intent"] = {"name": intent, "confirmationStatus": "NONE", "slots": slots or {}}
    if reason:
        request["reason"] = reason
    user = {"userId": "test-user"}
    application = {"applicationId": "test-app"}
    return {
        "version": "1.0",
        "session": {
            "new": kind == "LaunchRequest",
            "sessionId": "test-session",
            "application": application,
            "user": user,
            "attributes": copy.deepcopy(attributes or {}),
        },
        "context": {
            "System": {
                "application": application,
                "user": user,
                "device": {"deviceId": "test-device", "supportedInterfaces": {}},
            }
        },
        "request": request,
    }


def invoke(**kwargs):
    return skill.lambda_handler(envelope(**kwargs), None)
