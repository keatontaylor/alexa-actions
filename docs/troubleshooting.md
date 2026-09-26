# Troubleshooting and safe updates

## Find which stage fails

1. Confirm the hosting type. Self-managed Lambda needs the complete ZIP, a matching runtime/architecture and `lambda_function.lambda_handler`. Alexa-hosted builds need the source plus requirements in their `lambda` folder. A cloud resource-provisioning error occurs before this code runs; dependency changes cannot establish that Amazon provisioning is repaired. See [deployment/tests](testing.md).
2. Import and build the entire [interaction model for your locale](locales.md). Confirm development testing is enabled and the selected endpoint is deployed. In the simulator, say `open <your invocation name>` and inspect Skill I/O. Check that the application ID corresponds to your skill in both request context/session; compare it locally rather than posting the full envelope. Amazon describes [custom skill invocation](https://developer.amazon.com/en-US/docs/alexa/custom-skills/understanding-how-users-invoke-custom-skills.html).
3. Check the backend request/response summary. It logs request type, intent, locale, request ID, supported interface names, end-session flag and local completion state. HA calls log method/path/status. It does not log tokens, full request envelopes, recognized person/device IDs or helper content at normal log level. A 401 means authentication, a 404 on the helper URL means helper/base URL, and transport/invalid-state errors require fixing connectivity or helper JSON first. Read-only access from the Lambda to the helper must work before answers can post events.
4. Check the HA script trace and helper value. Use the correct [UI/file wrapper](home-assistant.md), keep the JSON within 255 characters and verify the launch integration/action. Watch `alexa_actionable_notification` in HA Developer Tools > Events. Responses are events; the question helper is not a response-history store. Managed mode additionally emits its [filtered result event](managed-notifications.md).
5. If the expected intent reaches Lambda and an event POST succeeds, check the automation's direct `event_data` filter. If the wrong intent/skill is reached, use Amazon's utterance profiler and simulator before changing response handlers. If only a physical device fails, record its model/generation, locale, launch method, actual request interfaces and whether an end callback arrives.

“You have no new notifications at this time” is not a prompt in this project's backend. That alone does not identify its source. For #275, establish whether this skill's LaunchRequest/application ID reached the selected endpoint before treating it as a helper or SDK error.

## Logs and personalization

For self-managed Lambda, the execution role needs CloudWatch log-writing permissions; the signed-in viewer also needs permission to read the log group. An IAM permission error opening logs is not proof the Italian model failed. Use the [AWS logging guide](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html) and the hosted console's own code/log controls for Alexa-hosted skills. Do not apply self-managed runtime/IAM instructions to a hosted service you cannot administer.

`event_person_id` appears only when Amazon recognizes and provides a person. Enable the skill's personalization/permissions and test consenting profiles with the simulator, following [Amazon personalization guidance](https://developer.amazon.com/en-US/docs/alexa/custom-skills/add-personalization-to-your-skill.html). Missing identity is supported and does not prevent Yes/No events. The skill receives structured intents/slots, not microphone audio, so it cannot filter TV noise or guarantee recognition. See [response metadata](response-handling.md).

## Fire TV Cube and screen devices

This backend emits no card, display or APL directive. A blank/default skill screen or TV wake after invoking a skill therefore needs launch-method/device evidence; the response code does not contain a tested HDMI/power-control fix. Compare manual invocation and the chosen HA launch action, record the generation and supportedInterfaces, and check Skill I/O/logs. Use an audio Echo for questions when keeping the TV asleep is essential. Do not assume that adding an APL document will prevent wake behavior. For missing silence callbacks, the HA-managed timeout can resolve the automation independently, but does not control the device's screen or microphone.

## Update and rollback

Back up your deployed backend, settings (`HOME_ASSISTANT_URL`, `VERIFY_SSL`, `TOKEN`, `DEBUG`, optional device metadata), exported interaction models and HA scripts/automations before updating. Keep credentials out of commits and issue comments. Apply the PRs in their stated dependency order; development artifacts are proposals, not published releases.

For self-managed Lambda, choose a supported runtime, use its matching complete artifact, restore your local settings, deploy to a development/test skill endpoint and run launch/answer/error checks. For Alexa-hosted, replace source/requirements in the development code, restore settings and let the hosted build install dependencies. Save/Build each full locale model; merge your custom selections/utterances back into that model before building. Avoid re-importing an old model that removes the new intents. Update HA helper/scripts with the proper wrapper and reload them; adding managed helpers needs a restart and moving side-effect consumers to the managed event.

Keep the previous source/artifact/models/HA configuration for rollback. Restore those together if necessary. When using a Lambda published version/alias, retain the prior version and use the test alias/endpoint flow you already manage. Do not publish a production skill or promote hosted development changes until their own simulator/live checks pass.

For Node-RED use the [local launch example](node-red.md) and [official setup documentation](https://nodered.org/docs/getting-started/), rather than relying on an unavailable third-party tutorial. Official Alexa/HA/AWS documentation checked 2026-09-26. Physical-device behaviors and Amazon server-side builds remain to be confirmed by testers.
