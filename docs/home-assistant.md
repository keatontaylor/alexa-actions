# Home Assistant setup

This repository contains an Alexa skill and HA scripts/blueprints. It is not a HACS custom integration. Adding it as an **Integration** custom repository produces the repository-structure error shown in recent reports: there is no `custom_components/<domain>` integration here. Install the skill and examples below manually. Alexa Media Player is a separate HACS integration. A `hacs.json` file alone cannot turn this repository into an integration; see [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/).

## Install the helper and script

Merge [configuration.yaml](../home-assistant/configuration.yaml) into your existing sections. If you use `script: !include scripts.yaml`, keep the helper under `input_text:` in configuration.yaml and put the script ID and nested body in scripts.yaml, without the `script:` wrapper. For the single-script UI YAML editor, paste [script-ui.yaml](../home-assistant/script-ui.yaml), which starts at `alias:`. Use the ID `activate_alexa_actionable_notification` so existing automations and the blueprint find it. Reload scripts after editing and verify the helper exists as `input_text.alexa_actionable_notification`.

Replace `REPLACE_WITH_YOUR_SKILL_ID` for Alexa Media Player. Call the script with `text`, `event_id`, and `alexa_device`. Existing `message` callers remain supported; when both are present, `text` wins. `suppress_confirmation` defaults to false. Questions are serialized with HA's `to_json` filter, preserving quotes, backslashes, and newlines; the entire JSON must fit the helper's 255-character maximum. Oversized or missing values fail before the helper is changed.

```yaml
action: script.activate_alexa_actionable_notification
data:
  text: Would you like the heating turned off?
  event_id: heating_question
  alexa_device: media_player.bedroom_echo
  suppress_confirmation: false
```

## Built-in Alexa Devices launch option

The current [Alexa Devices integration](https://www.home-assistant.io/integrations/alexa_devices/) supports `alexa_devices.send_text_command`. Select `transport: alexa_devices`, provide its HA `device_id`, and set the invocation name for your installed custom skill. This sends `open <invocation name>` to launch the skill, whose backend reads the helper. A Speak/Announce notification only speaks text and does not launch this question/answer skill.

```yaml
action: script.activate_alexa_actionable_notification
data:
  text: Did the test work?
  event_id: actionable.skill.test
  transport: alexa_devices
  device_id: YOUR_HOME_ASSISTANT_ALEXA_DEVICE_ID
  invocation_name: actionable notifications
  suppress_confirmation: true
```

The HA device ID is different from Amazon's request-envelope device ID. Configuration validation covers both launch branches with fake actions; account login, custom-skill routing, and physical devices still need owner testing.

## Responses and blueprint

Listen to `alexa_actionable_notification` in Developer Tools > Events. The public keys remain `event_id`, `event_response`, and `event_response_type`. Use `event_data` directly under the event trigger, as in [event-example.yaml](../home-assistant/event-example.yaml); do not nest another `event_type`/`event_data` inside it.

Import the [blueprint](../home-assistant/alexa_actions_skill_automation_template.yaml) and set its trigger helper, Echo entity, question, and unique event ID. Optional condition/blocking entities may be left empty. **Allow confirmation response** means Alexa says Okay; it is converted to the inverse `suppress_confirmation` flag. Empty optional actions are valid lists.

The basic script holds one pending question in one global helper. Starting another question before the first skill launch reads it can overwrite it. For reliable unanswered-question handling and serialized requests, use the separate managed example when available; neither the basic script nor the original blueprint can guarantee that Amazon sends a silence callback on every screen device.

## Authentication diagnostics

The Lambda must reach your external HA HTTPS URL. A 401 means check the linked/long-lived token; a 404 on `/api/states/input_text.alexa_actionable_notification` means check the helper and URL. Updating HA Cloud's account-linking settings cannot create a missing helper. In modern HA, Developer Tools **Actions** is where old tutorials' **Services** calls are run.

Based on the current [script syntax](https://www.home-assistant.io/docs/scripts/), [selectors](https://www.home-assistant.io/docs/blueprint/selectors/), [templating](https://www.home-assistant.io/docs/templating/), and [event triggers](https://www.home-assistant.io/docs/automation/trigger/), checked 2026-09-26. The runnable examples are checked using Home Assistant 2026.9.3's actual validators and script engine, without a live Amazon account.
