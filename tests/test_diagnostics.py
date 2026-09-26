from conftest import envelope, invoke, skill


def test_request_response_summary_omits_tokens_and_person_data(fake_ha, caplog):
    fake_ha.state["text"] = "Private question content"
    event = envelope()
    event["context"]["System"]["user"]["accessToken"] = "private-linked-token"
    event["context"]["System"]["person"] = {"personId": "private-person-id"}
    event["context"]["System"]["device"]["supportedInterfaces"] = {"AudioPlayer": {}, "Alexa.Presentation.APL": {}}
    skill.lambda_handler(event, None)
    logs = caplog.text
    assert "request type=LaunchRequest" in logs and "response id=test-request" in logs
    assert "AudioPlayer" in logs and "Alexa.Presentation.APL" in logs
    for private in [
        "private-linked-token",
        "private-person-id",
        "test-device",
        "Private question content",
        "test-only-token",
    ]:
        assert private not in logs


def test_http_error_summary_has_status_without_response_payload(fake_ha, caplog):
    fake_ha.get_status = 401
    fake_ha.raw_state = "private-response-body"
    invoke()
    assert "status=401" in caplog.text
    assert "ha_state=HaStateError" in caplog.text
    assert "private-response-body" not in caplog.text
