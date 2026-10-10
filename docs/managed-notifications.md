# Optional Home Assistant managed deadlines

## Multiple devices

Install the current shared [launcher](home-assistant.md), update this package, and restart HA for the new `input_text.alexa_actionable_group_silence` helper. Supply up to ten individual targets, not a speaker-group entity:

```yaml
action: script.activate_alexa_actionable_notification_managed
data:
  text: Is anyone home?
  event_id: occupancy_question
  timeout_seconds: 60
  targets:
    - transport: alexa_media
      alexa_device: media_player.kitchen
    - transport: alexa_devices
      device_id: YOUR_HA_DEVICE_ID
```

Launches are dispatched in order while the helper stays on the same question; sessions can overlap. The first non-silence answer wins. One silent device does not end the group: `ResponseNone` completes it when every distinct member reports silence or the deadline expires. Duplicate targets/callbacks are ignored. Group events carry a compact hashed `event_device_key` to count silence without enabling raw device IDs; missing identity waits for the deadline. Do not list one physical Echo through both integrations.

The queue advances after launch actions return and a result exists. An accepted action does not prove a delayed Amazon request has read the helper. Physical timing and Alexa+ routing need device testing; this does not create native speaker-group sessions. Use managed results for side effects; raw events still contain individual responses.

Set `audio_only: true` and mark screen targets with `screen: true` to exclude them. Invalid/all-screen selections stop before changing the helper. This avoids launching on configured screens; it does not change Fire Cube's screen or power behavior.

## Presence routing

Install [presence-routing.yaml](../home-assistant/presence-routing.yaml) as an HA package, or copy its script into your scripts configuration. It selects the first configured route whose sensor is `on`, otherwise a fallback. Unknown/unavailable sensors are not present. This uses explicit mappings and existing sensors, not automatic location discovery.

```yaml
action: script.activate_alexa_actionable_notification_presence
data:
  text: Would you like the lights off?
  event_id: lights_question
  audio_only: true
  routes:
    - presence_entity: binary_sensor.kitchen_occupied
      target:
        alexa_device: media_player.kitchen
    - presence_entity: binary_sensor.lounge_occupied
      target:
        alexa_device: media_player.fire_cube
        screen: true
  fallback:
    alexa_device: media_player.bedroom_echo
```

Audio-only routing skips marked screen routes and needs an audio fallback. The [presence blueprint](../home-assistant/presence-question-blueprint.yaml) stores these mappings; the [managed blueprint](../home-assistant/managed-question-blueprint.yaml) covers fixed single/multiple targets and both transports.

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
