import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const flow = JSON.parse(readFileSync(new URL("../home-assistant/node-red-launch.json", import.meta.url), "utf8"));
const code = flow.find(node => node.type === "function").func;
const credentials = { HA_URL: "https://test.invalid/", HA_TOKEN: "test-only-token", ALEXA_ENTITY: "media_player.test" };
const errors = [];
const execute = values => runInNewContext("(function () {" + code + "})()", {
  msg: {}, env: { get: key => values[key] }, node: { error: message => errors.push(message) }
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
console.log("Node-RED launch payload, missing configuration and status-only debug OK");
