# Notification response handling

## Standalone commands

Set `ENABLE_COMMANDS: true` in private settings (or environment variable `ENABLE_COMMANDS=true`) and rebuild the full locale model. Say `ask <invocation name> to do <command>` in English; the `Command` intent uses `CommandText`. Localized carrier samples are included in every model. Initial-session String/FreeText requests also use this opt-in path for older customizations.

Commands POST a separate **`alexa_actionable_command`** event with `command`, `intent` and Amazon `request_id`. They never read the notification helper or reuse its event ID. Optional person/device metadata follows the notification settings. An active notification must be answered/stopped first. Notification answers and no-response callbacks still require their launch snapshot.

Subscribe to the command event in HA or Node-RED and map permitted commands to your existing actions. Enable `INCLUDE_DEVICE_ID` and map Amazon IDs to HA entities for replies to the originating Echo; Amazon IDs are not HA device IDs. Repeated command requests carrying completion attributes are suppressed, but consumers should deduplicate `request_id` for side effects across platform retries. No command interprets arbitrary code or automatically invokes HA services.

## Configuration and ownership

Configuration precedence is deployed constants, optional private `lambda/settings.json`, then environment. Copy [settings.example.json](../lambda/settings.example.json) for the supported names; add your private token locally. `ALEXA_ACTIONS_CONFIG` selects an alternative file. Boolean values accept only true/false. The private file is ignored by Git. Hosted source deployments can use the file without editing Python; do not assume the hosted console offers environment settings. Keep private deployment artifacts private.

| File | Owner |
| --- | --- |
| `lambda_function.py` | Runtime defaults, settings, client injection and SDK registration |
| `configuration.py` | File/environment precedence and validation |
| `home_assistant.py` | HA transport, session snapshots and event delivery |
| `handlers.py` | Intent routing and spoken responses |
| `interceptors.py` | Localization and safe diagnostics |
| `schemas.py` | Notification data contract |

The entrypoint retains its existing `HomeAssistant`, HTTP-factory and settings seams. Install all backend files together; the split modules are included in deployment ZIPs.

On launch, the backend fetches the helper once and stores its question, event ID, confirmation flag and optional `request_id` in Alexa session attributes. Later intents and end callbacks use that snapshot. They do not fetch whichever question happens to be in the helper now. An intent/end callback without a launch snapshot cannot post an answer against the current helper. Deploy the backend, start a fresh skill session, and carry `sessionAttributes` when replaying test requests.

Answered and fallback/cancel/stop responses explicitly set `shouldEndSession: true`, including silent confirmations. After a successful HA POST the session is marked complete, so a later callback carrying those attributes does not emit another response. This is session-local protection, not durable exactly-once delivery across arbitrary platform retries or independent sessions. POST timeouts are not retried automatically because HA may already have accepted the event.

Selections respect suppression and report HA errors instead of claiming selection success after a failed POST. Missing or unresolved slots reprompt the original question without another helper fetch. Malformed/unavailable helper JSON, missing tokens, HTTP errors and network failures produce terminal configuration/connectivity messages. The error handler never makes another HA request. HTTP retries are disabled and connect/read timeouts are bounded to fit Alexa's response budget.

`SessionEndedRequest` returns no speech, cards or directives, as required by Amazon. A missing physical-device callback cannot be repaired by changing this handler: use the HA-managed timeout example when you need a deadline independent of Alexa's screen/session lifecycle.

The public response event stays `alexa_actionable_notification` with its existing `event_id`, `event_response`, and `event_response_type` keys/values. `event_person_id` is included only when Amazon supplies a recognized person. Enable personalization/permissions on the skill and test consenting profiles in the simulator. An absent person ID is normal; this code cannot identify an unrecognized speaker or change device noise suppression. Authentication continues to use the skill user's account-linking token rather than requiring person recognition.

Set `INCLUDE_DEVICE_ID = True` in the backend to opt into an `event_device_id` field from `context.System.device.deviceId`. This is an Amazon ID scoped to the skill, not a HA device-registry ID or Alexa Media Player entity. It is omitted by default. Optional helper `request_id` is echoed unchanged for correlation in the managed example.

Based on Amazon's current [session guidance](https://developer.amazon.com/en-US/docs/alexa/custom-skills/manage-skill-session-and-session-attributes.html), [request/response contract](https://developer.amazon.com/en-US/docs/alexa/custom-skills/request-and-response-json-reference.html), [personalization](https://developer.amazon.com/en-US/docs/alexa/custom-skills/add-personalization-to-your-skill.html), [SDK slot utilities](https://github.com/alexa/alexa-skills-kit-sdk-for-python/blob/master/ask-sdk-core/ask_sdk_core/utils/request_util.py), and [HA REST API](https://developers.home-assistant.io/docs/api/rest/), checked 2026-09-26. Tests use the real ASK SDK with fake HA HTTP; physical-screen timing and hosted deployment remain unverified.
