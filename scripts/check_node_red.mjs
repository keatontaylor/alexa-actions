import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const flow = JSON.parse(readFileSync(new URL("../home-assistant/node-red-launch.json", import.meta.url), "utf8"));
const code = flow.find(node => node.type === "function").func;
const credentials = { HA_URL: "https://test.invalid/", HA_TOKEN: "test-only-token", ALEXA_ENTITY: "media_player.test" };
const errors = [];
const execute = (values, msg = {}, source = code) => runInNewContext("(function () {" + source + "})()", {
  msg, env: { get: key => values[key] }, node: { error: message => errors.push(message) }
}, { timeout: 1000 });
const message = execute(credentials);
assert.equal(message.url, "https://test.invalid/api/services/script/activate_alexa_actionable_notification");
assert.equal(message.method, "POST");
assert.equal(message.headers.Authorization, "Bearer test-only-token");
assert.equal(message.headers["Content-Type"], "application/json");
assert.deepEqual(JSON.parse(JSON.stringify(message.payload)), {
  text: "Did the Node-RED question work?", event_id: "node_red_test",
  alexa_device: "media_player.test", suppress_confirmation: false
});
assert.equal(execute({}), null);
assert.equal(errors.length, 1);
assert.equal(flow.find(node => node.type === "inject").once, false);
assert.equal(flow.find(node => node.type === "debug").complete, "statusCode");
const native = execute({...credentials, ALEXA_TRANSPORT: "alexa_devices", ALEXA_DEVICE_ID: "ha-device"}, {payload: {text: "Native?", confirmation_yes: "Done", managed: true}});
assert.equal(native.payload.device_id, "ha-device");
assert.equal(native.payload.transport, "alexa_devices");
assert.equal(native.payload.confirmation_yes, "Done");
assert.equal(native.payload.alexa_device, undefined);
assert.ok(native.url.endsWith("_managed"));
const grouped = execute(credentials, {payload: {targets: [{alexa_device: "media_player.one"}, {device_id: "ha-two", transport: "alexa_devices"}]}});
assert.equal(grouped.payload.targets.length, 2);
assert.ok(grouped.url.endsWith("_managed"));
const sensorCode = flow.find(node => node.name === "Optional HA sensor read").func;
const reading = execute({...credentials, HA_SENSOR: "sensor.temperature"}, {payload: {event_id: "temperature"}}, sensorCode)[0];
assert.ok(reading.url.endsWith("/api/states/sensor.temperature"));
assert.equal(reading.method, "GET");
reading.statusCode = 200;
reading.payload = {state: "21", attributes: {unit_of_measurement: "C"}};
assert.ok(execute(credentials, reading).payload.text.includes("21 C"));
assert.equal(execute(credentials, {sensorRead: true, statusCode: 500, payload: {}}), null);
console.log("Node-RED launch payload, missing configuration and status-only debug OK");
