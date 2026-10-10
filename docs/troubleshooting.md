# Troubleshooting and safe updates

## Find which stage fails

1. Confirm the hosting type. Self-managed Lambda needs the complete ZIP, a matching runtime/architecture and `lambda_function.lambda_handler`. Alexa-hosted builds need the source plus requirements in their `lambda` folder. A cloud resource-provisioning error occurs before this code runs; dependency changes cannot establish that Amazon provisioning is repaired. See [deployment/tests](testing.md).
2. Import and build the entire [interaction model for your locale](locales.md). Confirm development testing is enabled and the selected endpoint is deployed. In the simulator, say `open <your invocation name>` and inspect Skill I/O. Check that the application ID corresponds to your skill in both request context/session; compare it locally rather than posting the full envelope. Amazon describes [custom skill invocation](https://developer.amazon.com/en-US/docs/alexa/custom-skills/understanding-how-users-invoke-custom-skills.html).
3. Check the backend request/response summary. It logs request type, intent, locale, request ID, supported interface names, end-session flag and local completion state. HA calls log method/path/status. It does not log tokens, full request envelopes, recognized person/device IDs or helper content at normal log level. A 401 means authentication, a 404 on the helper URL means helper/base URL, and transport/invalid-state errors require fixing connectivity or helper JSON first. Read-only access from the Lambda to the helper must work before answers can post events.
4. Check the HA script trace and helper value. Use the correct [UI/file wrapper](home-assistant.md), keep the JSON within 255 characters and verify the launch integration/action. Watch `alexa_actionable_notification` in HA Developer Tools > Events. Responses are events; the question helper is not a response-history store. Managed mode additionally emits its [filtered result event](managed-notifications.md).
5. If the expected intent reaches Lambda and an event POST succeeds, check the automation's direct `event_data` filter. If the wrong intent/skill is reached, use Amazon's utterance profiler and simulator before changing response handlers. If only a physical device fails, record its model/generation, locale, launch method, actual request interfaces and whether an end callback arrives.

“You have no new notifications at this time” is not a prompt in this project's backend. That alone does not identify its source. For #275, establish whether this skill's LaunchRequest/application ID reached the selected endpoint before treating it as a helper or SDK error.

## Alexa-hosted dependency failures

[Issue #286](https://github.com/keatontaylor/alexa-actions/issues/286) reports a deployment failure that disappeared after changing urllib3. [Discussion #274](https://github.com/keatontaylor/alexa-actions/discussions/274) separately reports Python 3.8 and OpenSSL 1.0.2k on a hosted skill. `urllib3>=2.6,<3` cannot install on Python 3.8, and earlier v2 releases that support Python 3.8 still require OpenSSL 1.1.1 or later to import. Use the complete updated `lambda/requirements.txt`, which selects `urllib3>=1.26.20,<2` below Python 3.10. Do not use an unbounded `urllib3>=1.26.20`; it can resolve to v2. Restore your private settings, then save and deploy the development backend.

The HTML/OAuth redirect shown in #286 alone does not identify a backend exception. If deployment still fails, establish whether it fails before the Code tab exists, while pip installs requirements, or when Lambda imports the handler; record the dependency error and hosting/runtime details. The legacy urllib3 branch is [unmaintained](https://urllib3.readthedocs.io/en/stable/v2-migration-guide.html). Use the self-managed Python 3.13 route for maintained urllib3; the hosted compatibility constraint does not upgrade Amazon's Python/OpenSSL.

## Alexa+ and launch methods

[Discussion #274](https://github.com/keatontaylor/alexa-actions/discussions/274) includes an October 2026 report from an en-AU Echo Dot: a spoken launch reached `LaunchRequest`, then `AMAZON.YesIntent`, and posted the HA event. An HA `alexa_devices.send_text_command` launch played the question with `shouldEndSession: false`, but the spoken Yes never reached the skill; Alexa+ responded independently and sent a delayed `SessionEndedRequest` roughly four minutes later. Both launches reported the same locale and interface list. This is evidence of a launch/routing difference on that tested setup, not proof that all Alexa+ devices or launch integrations behave alike. The repository has no verified fix for that routing behavior.

Compare these paths with the same helper question and device:

1. Say `open <invocation name>` aloud and answer Yes. Confirm LaunchRequest, YesIntent and a successful HA event POST in the safe summary logs.
2. Launch through your configured HA integration and answer Yes. Check whether any IntentRequest arrives after the question; a successful helper GET alone does not prove the answer can reach the skill.
3. If Alexa answers with its own notification message, try a distinct invocation name without `notifications`, save/build the model and update the HA launch name to match. Interception of names containing `notifications` is also reported in #274; this is a troubleshooting experiment, not a guaranteed fix.

If only the HA launch loses the answer, use the spoken launch or a device/launch method you have verified. The backend cannot post a Yes/No response it never receives. [HA-managed deadlines](managed-notifications.md) can resolve the automation with `ResponseNone` without waiting for Amazon's delayed callback, but cannot restore microphone routing. Include device generation, locale, Alexa+ status, integration/action, request types, `shouldEndSession` and HA status codes when reporting results; keep tokens and full request envelopes private.

## Logs and personalization

For self-managed Lambda, the execution role needs CloudWatch log-writing permissions; the signed-in viewer also needs permission to read the log group. An IAM permission error opening logs is not proof the Italian model failed. Use the [AWS logging guide](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html) and the hosted console's own code/log controls for Alexa-hosted skills. Do not apply self-managed runtime/IAM instructions to a hosted service you cannot administer.

`event_person_id` appears only when Amazon recognizes and provides a person. Enable the skill's personalization/permissions and test consenting profiles with the simulator, following [Amazon personalization guidance](https://developer.amazon.com/en-US/docs/alexa/custom-skills/add-personalization-to-your-skill.html). Missing identity is supported and does not prevent Yes/No events. The skill receives structured intents/slots, not microphone audio, so it cannot filter TV noise or guarantee recognition. See [response metadata](response-handling.md).

## Fire TV Cube and screen devices

For a tested routing workaround, use managed/presence questions with `audio_only: true`, mark Cube/TV targets `screen: true`, and provide an audio fallback. The HA engine checks that these devices are excluded from launches. This avoids interrupting that screen by launching the question elsewhere; it does not preserve video while the Cube itself runs the skill, and no physical screen/power fix is claimed.

This backend emits no card, display or APL directive. A blank/default skill screen or TV wake after invoking a skill therefore needs launch-method/device evidence; the response code does not contain a tested HDMI/power-control fix. Compare manual invocation and the chosen HA launch action, record the generation and supportedInterfaces, and check Skill I/O/logs. Use an audio Echo for questions when keeping the TV asleep is essential. Do not assume that adding an APL document will prevent wake behavior. For missing silence callbacks, the HA-managed timeout can resolve the automation independently, but does not control the device's screen or microphone.

## Update and rollback

Back up your deployed backend, settings (`HOME_ASSISTANT_URL`, `VERIFY_SSL`, `TOKEN`, `DEBUG`, optional device metadata), exported interaction models and HA scripts/automations before updating. Keep credentials out of commits and issue comments. Apply the PRs in their stated dependency order; development artifacts are proposals, not published releases.

For self-managed Lambda, choose a supported runtime, use its matching complete artifact, restore your local settings, deploy to a development/test skill endpoint and run launch/answer/error checks. For Alexa-hosted, replace source/requirements in the development code, restore settings and let the hosted build install dependencies. Save/Build each full locale model; merge your custom selections/utterances back into that model before building. Avoid re-importing an old model that removes the new intents. Update HA helper/scripts with the proper wrapper and reload them; adding managed helpers needs a restart and moving side-effect consumers to the managed event.

Keep the previous source/artifact/models/HA configuration for rollback. Restore those together if necessary. When using a Lambda published version/alias, retain the prior version and use the test alias/endpoint flow you already manage. Do not publish a production skill or promote hosted development changes until their own simulator/live checks pass.

For Node-RED use the [local launch example](node-red.md) and [official setup documentation](https://nodered.org/docs/getting-started/), rather than relying on an unavailable third-party tutorial. Official Alexa/HA/AWS documentation checked 2026-09-26. Physical-device behaviors and Amazon server-side builds remain to be confirmed by testers.
