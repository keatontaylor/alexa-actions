# Set up the Alexa skill

This walkthrough covers the current repository backend and the Alexa developer console. Use it with the [Home Assistant setup](home-assistant.md). The older wiki can help explain the project, but its template names, Python versions, and Home Assistant Services screens may differ from the current interfaces. Official documentation was checked on 2026-09-26; the Amazon account and cloud deployment steps still need testing in your own development skill.

## 1. Prepare Home Assistant and choose hosting

Install the helper and script from [Home Assistant setup](home-assistant.md). Confirm that `input_text.alexa_actionable_notification` exists before testing the skill. The backend must be able to reach Home Assistant's REST API; a URL that works only on your home network will not work from an ordinary cloud Lambda.

For the standard backend, use your reachable Home Assistant HTTPS base URL, without `/api` or a helper path. Create a long-lived access token under your HA user profile's **Security** tab, following [HA authentication](https://www.home-assistant.io/docs/authentication/). Keep the token in your private deployed configuration. The static-token path is sufficient for initial testing; account linking is only needed if you choose to supply the token that way.

Choose one hosting route:

| Route | Backend installation | Network requirement |
| --- | --- | --- |
| Alexa-hosted Python | Source and requirements in the console's `lambda` folder; Amazon installs dependencies | HA must be reachable from the hosted service |
| Self-managed AWS Lambda | Complete Python 3.13 / x86_64 ZIP from this repository's Build Linux artifacts | HA must be reachable from your Lambda |
| Private HA through Tailscale | Separate container/proxy deployment, described below | Both HA and the backend must actually connect to the tailnet |

See [deployment and package tests](testing.md) for artifact selection. A fork's Docker image and this repository's ZIP are different deployment routes.

## 2. Create a Custom skill

Open the [Alexa developer console](https://developer.amazon.com/alexa/console/ask), create a skill, and select the language matching your device or simulator. Choose the **Custom** interaction model. For hosting, choose **Alexa-Hosted (Python)** if Amazon will manage the backend, or **Provision your own** for your own Lambda. Select an available starter template and replace its backend/model in the following steps; the setup does not depend on a template being named Python or Customize.

Amazon documents the [hosted creation flow](https://developer.amazon.com/en-US/docs/alexa/hosted-skills/alexa-hosted-skills-create.html) and the [self-managed Lambda flow](https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html) separately. If hosted resource creation fails before the code editor is available, installing dependencies cannot repair that provisioning step.

## 3. Import the full interaction model

On the skill's **Build** page, select the appropriate language and open **Interaction Model > JSON Editor**. Upload or paste the complete matching file from [interactionModels/custom](../skill-package/interactionModels/custom), then save and build the model. Keep the file's intent and slot definitions together, including the built-in Yes, No, Stop, Cancel, Help, and Fallback intents. Edit the invocation name if desired and use that same name in HA's Alexa Devices launch settings.

Amazon's [Build page reference](https://developer.amazon.com/en-US/docs/alexa/devconsole/build-your-skill.html) describes the model editor and Endpoint configuration. If your locale has no model file, an English backend fallback does not create a voice model for it. See [locales and free-text answers](locales.md) for supported models and answer phrases.

## 4. Install the backend

### Alexa-hosted Python

In the **Code** tab, replace the starter backend with every source file from this repository's [lambda folder](../lambda), including `language_strings.json` and `requirements.txt`. Configure `HOME_ASSISTANT_URL`, `TOKEN`, and `VERIFY_SSL` at the top of your private deployed `lambda_function.py`; keep SSL verification enabled for a valid HTTPS endpoint. Save and deploy the development backend. Amazon runs pip from requirements during deployment; do not upload a self-managed deployment ZIP as the hosted source tree. The hosted service manages its runtime.

### Self-managed Lambda

Create a Python 3.13 / x86_64 function in an appropriate AWS region for your Alexa users, with its execution role able to write CloudWatch logs. Install the complete tested ZIP with the handler `lambda_function.lambda_handler`, and restore your private backend settings before testing. If building locally, configure a private copy of the source before packaging and keep credentials out of Git. These settings are Python constants in the current upstream backend; `HA_URL` and `HA_TOKEN` environment variables from MelleD's fork do not configure this ZIP.

Copy your Skill ID from the skill list in the Alexa developer console. Add an **Alexa Skills Kit** trigger in the Lambda console and restrict it to that Skill ID. Copy the Lambda function ARN into **Build > Endpoint > AWS Lambda ARN** in the Alexa console and save. The skill endpoint is the Lambda ARN; the HA base URL is a separate backend setting. Follow [Amazon's trigger and endpoint instructions](https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html) for the current screens and region choices.

## 5. Test before connecting automations

Enable development testing on the console's **Test** page and select the matching locale. Set a short test question in the HA helper, for example `{"text":"Did the test work?","event":"setup_test","suppress_confirmation":true}`, then say or type `open <invocation name>` in the simulator. Answer Yes and listen for `alexa_actionable_notification` in HA **Developer Tools > Events**. Expect `event_id: setup_test`, `event_response: ResponseYes`, and `event_response_type: ResponseYes`.

Once manual simulator invocation works, run `script.activate_alexa_actionable_notification` with a test device using HA **Developer Tools > Actions**. For Alexa Media Player, insert your Skill ID into the script. For the built-in Alexa Devices integration, use its HA device ID and the installed invocation name. The simulator covers the backend without an Echo; a physical launch integration still needs a device owner to test it. See [device-free tests](testing.md) and [troubleshooting](troubleshooting.md).

## Private Home Assistant through Tailscale

[MelleD's fork](https://github.com/MelleD/alexa-actions/tree/9e805dffe371656745a64ac2b3a6ba75d4d548ee) contributed a useful Lambda container and private-network walkthrough. Its guide is a reference for a separate deployment route, rather than instructions for the current upstream ZIP. This repository does not yet ship a Tailscale entrypoint, image-publishing workflow, or SOCKS-aware HTTP client.

The [HA Tailscale integration](https://www.home-assistant.io/integrations/tailscale/) only monitors tailnet devices. Install a real Tailscale client on the HA host, or arrange an appropriate subnet route. The Lambda also needs tailnet connectivity. [Tailscale's Lambda guide](https://tailscale.com/docs/install/cloud/aws/aws-lambda) uses userspace networking for this; the application must explicitly use the configured SOCKS/HTTP proxy. Merely setting `ALL_PROXY` on the current upstream `urllib3.PoolManager` does not enable SOCKS support.

For a container deployment, keep ECR and Lambda in the same region, use a matching single architecture, and keep image credentials private, following [AWS container requirements](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html). Repository names and regions are deployment choices; `ha-custom-lambda-tailscale` and `eu-west-1` are values in the fork's workflow, not universal AWS requirements. [AWS OIDC roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html) can supply temporary CI credentials instead of copying long-lived AWS access keys into a guide.

Plan how new Lambda containers authenticate and how expired keys are replaced. Ephemeral device cleanup and auth-key expiry are different settings; [Tailscale auth-key documentation](https://tailscale.com/docs/features/access-control/auth-keys) also describes reusable keys and programmatic generation with OAuth. The fork's statement that automatic key creation is impossible should not be carried into a current guide.

Keep initialization and API requests within Alexa's approximately eight-second full-response window. Increasing the Lambda or HTTP timeout to ten seconds does not extend it, per [Amazon's response timing](https://developer.amazon.com/en-US/docs/alexa/custom-skills/send-the-user-a-progressive-response.html). A maintained Tailscale port needs bounded startup, current dependencies, correctly parsed settings, proxy timeouts/TLS behavior, and cold/warm-container tests before being offered as an upstream deployment option. The [fork review](fork-review-2026-09-26.md) records the remaining work.
