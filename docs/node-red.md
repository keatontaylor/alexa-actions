# Node-RED launch example

## Transports, sensors and managed questions

The imported flow supports both transports. For official Alexa Devices, set `ALEXA_TRANSPORT=alexa_devices`, `ALEXA_DEVICE_ID` to its HA device ID, and optionally `ALEXA_INVOCATION`. Alexa Media Player remains the default. Both call the HA scripts and shared launcher; no Alexa palette is required.

An upstream node can set `msg.payload` to an options object with `text`, `event_id`, transport/target overrides, suppression or custom confirmations. `managed: true` selects the managed script; a `targets` list selects it automatically. Managed questions support `timeout_seconds` and `audio_only` and require the managed package.

Set optional `HA_SENSOR=sensor.lounge_temperature` to read its state via HA REST before building a question. The flow includes the required core HTTP node, preserves question options during the GET, includes the reading/unit, and stops on failed/unavailable reads. Edit the sensor sentence for your wording, or use an existing state node and JavaScript:

```javascript
msg.payload = {
  text: "The temperature is " + msg.sensor_state + " degrees. Turn off the heating?",
  event_id: "temperature_question",
  managed: true,
  confirmation_yes: "Turning off the heating."
};
return msg;
```

HA's `states()` Jinja function is not a Node-RED JSONata function. Resolve the sensor through the supplied REST flow or a configured HA state node first.

Use the [official Node-RED setup guide](https://nodered.org/docs/getting-started/) instead of the unavailable external tutorial reported in #269. Import [node-red-launch.json](../home-assistant/node-red-launch.json) into Node-RED. It uses core Inject, Function, HTTP Request and Debug nodes; no extra palette package is required for this launch example.

Install the [HA helper/script](home-assistant.md) and skill first. Configure the Node-RED environment variables `HA_URL`, `HA_TOKEN` (a HA long-lived access token) and `ALEXA_ENTITY` (the Alexa Media Player entity). Set these in your own runtime/environment, not in the exported flow. Edit the question and event ID in **Build HA script call**, deploy, and press the manual Inject button. It calls HA's script REST action with a JSON body. The flow has no automatic startup trigger, and Debug shows only HTTP status, not the message containing its Authorization header.

A successful HTTP status means the HA script call completed; it does not prove voice recognition or a returned answer. To consume answers, listen for `alexa_actionable_notification` and filter its `event_id`/`event_response_type` through your existing HA event connection, or use the maintained [HA response automation example](../home-assistant/event-example.yaml). For the managed deadline option use its different script and result event as described in [managed mode](managed-notifications.md). This core-only example does not install an authenticated WebSocket subscription or your home's automations for you.

The flow's request construction and missing-configuration behavior are tested with Node.js and test-only values. Live Node-RED/HA/Alexa delivery still needs your configured accounts. Based on the [HA REST API](https://developers.home-assistant.io/docs/api/rest/) and [official Node-RED HTTP recipe](https://cookbook.nodered.org/http/post-json-data-to-a-flow), checked 2026-09-26.
