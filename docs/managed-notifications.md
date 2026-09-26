# Optional Home Assistant managed deadlines

Use this example when silence on an Echo Show/Fire TV does not cause Amazon to send `SessionEndedRequest`. HA owns the deadline, rather than relying on a device callback. It also serializes questions sharing the single skill helper and filters late/duplicate responses by a per-call request ID.

Deploy the session-context backend first (the helper's `request_id` must be echoed in response events). Keep the original `input_text.alexa_actionable_notification` helper. Install [managed-notifications.yaml](../home-assistant/managed-notifications.yaml) as a [HA package](https://www.home-assistant.io/docs/configuration/packages/), or merge its counter/input_text/script/automation sections into your existing configuration without duplicate top-level keys. Restart HA after adding helpers. Replace the skill-ID placeholder for Alexa Media Player. Do not simultaneously call the basic script/blueprint or another producer that overwrites the same question helper.

Call `script.activate_alexa_actionable_notification_managed` with the same fields as the basic script and `timeout_seconds` (default 60; choose enough time for the question plus an answer). It supports both Alexa Media Player and official Alexa Devices launch methods.

```yaml
action: script.activate_alexa_actionable_notification_managed
data:
  text: Is someone still in the cellar?
  event_id: cellar_question
  alexa_device: media_player.cellar_echo
  timeout_seconds: 60
  suppress_confirmation: true
```

For automations using this mode, listen to **`alexa_actionable_notification_managed`**, with the original event_id/event_response/event_response_type fields and the new request_id. HA templates may normalize numeric/JSON text in the top-level `event_response`; the added `raw_event` dictionary retains the original payload and types if your actions depend on them. Move their raw-event triggers to this event; do not consume both raw and managed events for the same action. The basic blueprint still listens to raw events and should not be combined with this managed producer.

The queued script allocates an ID from the invocation context and an incrementing counter, writes pending identity before launching, and waits on a completion helper. The queued broker accepts only matching event/request IDs, clears pending identity before forwarding, and forwards the first response fields and person/device metadata (null when absent). A deadline competes through that same broker as ResponseNone. A response arriving during launch is retained in helper state, so it cannot be lost by registering an event waiter after the launch. Repeated or old-session events do not become results for the next question, even if its event_id is reused.

The timeout event is internal (`alexa_actionable_notification_timeout`); it does not synthesize another raw Alexa response. Raw subscribers retain their existing behavior. Outgoing launch failures are logged by HA and allowed to reach the managed deadline. Invalid/oversized payloads fail before launch. The entire question JSON, including request_id, still must fit 255 characters, so managed questions have less room for text.

This is one serialized queue (maximum 10 waiting/running calls), not parallel per-device storage. A HA restart/reload/cancel interrupts waits; pending/completion helpers initialize empty and in-flight deadlines are not restored. It is not durable exactly-once delivery across HA crashes, nor can it stop a device from presenting an old question. Use the managed result for side effects; the raw event remains observable for diagnosis.

Validated with Home Assistant 2026.9.3's script engine and fake launch actions, including immediate replies, timeout, late/duplicate replies, reused event IDs and overlapping calls. Physical-device launch/screen behavior still needs owner testing. Based on current [HA waits/events](https://www.home-assistant.io/docs/scripts/), [script modes](https://www.home-assistant.io/integrations/script/), [counters](https://www.home-assistant.io/integrations/counter/), and [Amazon sessions](https://developer.amazon.com/en-US/docs/alexa/custom-skills/manage-skill-session-and-session-attributes.html), checked 2026-09-26.
