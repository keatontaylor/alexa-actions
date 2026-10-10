"""Real loopback HTTP/TLS with the production urllib3 pool on both runtimes."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import ssl
import threading
import time

import pytest
import urllib3

from conftest import envelope, skill


@contextmanager
def server(tls=False):
    state = {"text": "HTTP question?", "event": "wire_event", "request_id": "wire_request"}
    calls, events = [], []
    faults = {"get": 200, "post": 200, "body": None, "delay": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, method):
            calls.append((method, self.path, self.headers.get("Authorization")))
            time.sleep(faults["delay"])
            status = faults[method.lower()]
            if method == "POST":
                event = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if status == 200:
                    events.append(event)
            body = faults["body"] if faults["body"] is not None else json.dumps({"state": json.dumps(state)})
            self.send_response(status)
            self.send_header("Content-Length", str(len(body.encode())))
            self.end_headers()
            try:
                self.wfile.write(body.encode())
            except (BrokenPipeError, ConnectionResetError):
                pass  # Expected after the client's timeout closes its socket.

        def do_GET(self):
            self.respond("GET")

        def do_POST(self):
            self.respond("POST")

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    if tls:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        fixtures = Path(__file__).parent / "fixtures"
        context.load_cert_chain(fixtures / "localhost-cert.pem", fixtures / "localhost-key.pem")
        http.socket = context.wrap_socket(http.socket, server_side=True)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"{'https' if tls else 'http'}://127.0.0.1:{http.server_port}", state, calls, events, faults
    finally:
        http.shutdown()
        http.server_close()
        worker.join(timeout=5)


@pytest.fixture
def wire(monkeypatch):
    # Do not replace _init_http_pool: this fixture exercises the production pool.
    monkeypatch.setattr(skill, "TOKEN", "wire-only-token")
    with server() as running:
        monkeypatch.setattr(skill, "HOME_ASSISTANT_URL", running[0])
        yield running[1:]


def test_real_http_preserves_snapshot_and_headers(wire):
    state, calls, events, _ = wire
    launched = skill.lambda_handler(envelope(), None)
    assert "HTTP question?" in launched["response"]["outputSpeech"]["ssml"]
    state.update(text="New question", event="new_event", request_id="new_request")
    reply = skill.lambda_handler(envelope("IntentRequest", "AMAZON.YesIntent", launched["sessionAttributes"]), None)
    assert events[0]["event_id"] == "wire_event" and events[0]["request_id"] == "wire_request"
    assert calls == [
        ("GET", "/api/states/input_text.alexa_actionable_notification", "Bearer wire-only-token"),
        ("POST", "/api/events/alexa_actionable_notification", "Bearer wire-only-token"),
    ]
    skill.lambda_handler(
        envelope("SessionEndedRequest", attributes=reply["sessionAttributes"], reason="USER_INITIATED"), None
    )
    assert len(events) == 1


@pytest.mark.parametrize("status", [301, 401, 404, 429, 500, 503])
def test_real_http_failed_get_does_not_create_snapshot(wire, status):
    _, calls, events, faults = wire
    faults["get"] = status
    reply = skill.lambda_handler(envelope(), None)
    assert str(status) in reply["response"]["outputSpeech"]["ssml"]
    assert skill.SESSION_KEY not in reply["sessionAttributes"]
    assert len(calls) == 1 and not events  # No retry or redirect request.


@pytest.mark.parametrize("status", [401, 500, 503])
def test_real_http_failed_post_can_be_retried_by_a_new_intent(wire, status):
    _, calls, events, faults = wire
    launched = skill.lambda_handler(envelope(), None)
    faults["post"] = status
    reply = skill.lambda_handler(envelope("IntentRequest", "AMAZON.NoIntent", launched["sessionAttributes"]), None)
    assert not reply["sessionAttributes"][skill.COMPLETED_KEY]
    assert not events and len(calls) == 2
    faults["post"] = 200
    retry = skill.lambda_handler(envelope("IntentRequest", "AMAZON.NoIntent", reply["sessionAttributes"]), None)
    assert retry["sessionAttributes"][skill.COMPLETED_KEY] and len(events) == 1


@pytest.mark.parametrize("body", ["not JSON", "{}", '{"state":"unavailable"}', '{"state":"[]"}'])
def test_real_http_invalid_helper(wire, body):
    _, _, events, faults = wire
    faults["body"] = body
    reply = skill.lambda_handler(envelope(), None)
    assert skill.SESSION_KEY not in reply["sessionAttributes"] and not events


def test_real_http_deadline_without_retries(wire):
    _, calls, events, faults = wire
    faults["delay"] = 2.5
    before = time.monotonic()
    reply = skill.lambda_handler(envelope(), None)
    assert time.monotonic() - before < 4
    assert skill.SESSION_KEY not in reply["sessionAttributes"]
    assert len(calls) == 1 and not events


@pytest.mark.parametrize("verify", [True, False])
def test_real_tls_rejects_untrusted_certificate_by_default(monkeypatch, verify):
    monkeypatch.setattr(skill, "VERIFY_SSL", verify)
    monkeypatch.setattr(skill, "TOKEN", "wire-only-token")
    with server(tls=True) as (url, _, calls, _, _):
        monkeypatch.setattr(skill, "HOME_ASSISTANT_URL", url)
        if verify:
            reply = skill.lambda_handler(envelope(), None)
            assert skill.SESSION_KEY not in reply["sessionAttributes"] and not calls
        else:
            with pytest.warns(urllib3.exceptions.InsecureRequestWarning):
                reply = skill.lambda_handler(envelope(), None)
            assert skill.SESSION_KEY in reply["sessionAttributes"] and len(calls) == 1
