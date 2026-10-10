# Testing without an Echo

The local suite uses the real Amazon ASK SDK and request envelopes. Fast tests use a fake HTTP boundary; transport tests use actual loopback HTTP and TLS servers. The Docker simulation connects real Node-RED, a packaged skill, and the actual Home Assistant script engine. None require an Alexa device, Amazon credentials, a Home Assistant token, or access to a live home.

```sh
python -m venv .venv
# Activate the environment for your OS.
python -m pip install -r requirements-test.txt
python -m pytest --cov --cov-branch --cov-config=pyproject.toml --cov-report=term-missing --junitxml=reports/junit.xml
python scripts/build_package.py --kind pure
python scripts/check_package.py dist/AlexaActionsNoBinaryLinux.zip
```

Each PR builds both ZIPs on Linux with Python 3.13 and tests the extracted ZIP with site packages disabled. Download its artifacts from the **CI** run. Each ZIP also runs through the Docker HTTP simulation. The binary artifact targets self-managed Lambda Python 3.13 / x86_64. The pure artifact contains no native extensions. All dependencies, including the ASK SDK, are installed into the package; uploading only `lambda_function.py` is insufficient. Build packages with Python 3.13; the builder rejects a different interpreter rather than resolving the wrong runtime's dependency markers.

For a self-managed AWS Lambda, upload the ZIP directly and set the handler to `lambda_function.lambda_handler`. Its files are at the ZIP root, per the [AWS Python deployment guide](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html). Use a currently supported runtime from [AWS's runtime table](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html); Python 3.13 is the runtime tested here. A binary package for another Python version or architecture must be rebuilt for that target.

For **Alexa-hosted** skills, use the source files and `requirements.txt` in the console's `lambda` folder. Amazon runs pip during the hosted build. Alexa controls the hosted runtime; changing a self-managed Lambda setting is not a hosted-runtime upgrade procedure. See [Create and manage Alexa-hosted skills](https://developer.amazon.com/en-US/docs/alexa/hosted-skills/alexa-hosted-skills-create.html). The project uses [ASK SDK core](https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/set-up-the-sdk.html) without its optional DynamoDB adapter.

CI also installs the complete test dependencies and runs the SDK suite on Python 3.8, matching the documented hosted Python version. The requirements select urllib3 1.26 for that legacy runtime and v2 for modern Python. A separate subprocess import check simulates the reported OpenSSL 1.0.2k version metadata to catch urllib3's incompatible import guard. This is an import compatibility test; it does not run the real hosted OpenSSL library or prove a TLS handshake or Amazon deployment. Repeat the install and `pytest tests` commands above in a Python 3.8 environment to run that check locally. Self-managed release ZIPs remain Python 3.13 artifacts.

The [Alexa simulator](https://developer.amazon.com/en-US/docs/alexa/devconsole/alexa-simulator.html) can test speech/text, routing, session attributes, and backend requests without a device. Import and build the complete interaction model for the selected locale, enable development testing, deploy the backend, and inspect **Skill I/O**. With a test HA helper, launch the skill and try Yes, No, a number, a duration, a selection, Stop, and silence. Also change the helper while an earlier question is open and check that its response retains its original event ID.

The simulator and local tests cannot establish Fire TV power behavior, far-field recognition with background noise, device-specific microphone/screen timing, or whether every physical device sends `SessionEndedRequest`. Those require reports from device owners. No physical-device validation is claimed by a passing local suite.

Official documentation checked on 2026-09-26. Software checks do not prove an Alexa-hosted deployment or live event delivery.

## Docker checks for current HA

The official HA image contains the actual validators and script engine. Run these commands from the repository (PowerShell/Linux shells both support the quoted current-directory mount):

```sh
docker run --rm --network none --entrypoint python --mount "type=bind,source=${PWD},target=/repo,readonly" ghcr.io/home-assistant/home-assistant:2026.9.3 /repo/scripts/check_home_assistant.py
docker run --rm --network none --entrypoint python --mount "type=bind,source=${PWD},target=/repo,readonly" ghcr.io/home-assistant/home-assistant:2026.9.3 /repo/scripts/check_managed_notifications.py
node scripts/check_node_red.mjs
```

These use temporary HA state and fake outgoing launch actions. No real home, Alexa account or device is contacted. The fast Node-RED check executes exported Function nodes; the Docker simulation below additionally runs the Function and HTTP Request nodes in the real Node-RED runtime.

## Full software simulation

Build both packages with Python 3.13, then run from the repository root:

```sh
python scripts/build_package.py --kind pure
python scripts/build_package.py --kind binary
docker compose -f tests/simulation/compose.yaml up --abort-on-container-exit --exit-code-from home-assistant
docker compose -f tests/simulation/compose.yaml logs --no-color
docker compose -f tests/simulation/compose.yaml down --volumes --remove-orphans
```

The default tests the pure ZIP. Set `PACKAGE_NAME=AlexaActionsWithBinaryLinux.zip` in your shell and repeat to test the binary ZIP. In PowerShell use `$env:PACKAGE_NAME = 'AlexaActionsWithBinaryLinux.zip'`. The binary scenario requires an x86_64 Docker engine. The Docker images are pinned by digest: Python 3.13, HA 2026.9.3 and Node-RED 5.0.8. Pulling images requires internet access; scenarios run on an [internal Compose network](https://docs.docker.com/compose/how-tos/networking/#internal-networks), with no published ports, private credentials or access to a real home. Repository mounts are read-only; temporary state is discarded when containers stop.

The chain is: exported Node-RED flow -> HTTP script service -> HA managed script/launcher -> simulated Echo request envelope -> packaged ASK SDK -> actual urllib3 GET/POST -> HA state/event bus -> managed broker result. The simulation replaces only Node-RED's manual Inject/Debug endpoints, Alexa launch services, and the HA REST/auth adapter. It checks bearer headers but does not boot HA's production authentication server. It uses the real YAML, templates, scripts, queues, session snapshots and broker.

Scenarios cover Yes/No, custom and suppressed confirmations, numeric/string replies, late and duplicate callbacks, overall silence deadlines, two-device groups across both launch methods, distinct-device silence, stale request IDs, failed event delivery, unauthorized/missing/server-error states, malformed helpers, bounded HTTP timeouts, and opt-in standalone commands. The separate HA checks cover presence routing, blueprints, escaped/oversized input, immediate replies and queued overlap. SDK tests cover all locales and intent types. Loopback TLS tests reject an untrusted certificate by default and check the explicit verification override.

This adapter invokes `lambda_handler` with ASK envelopes; it does not emulate AWS Lambda's runtime API, provision a skill, test Amazon speech recognition, reproduce legacy hosted OpenSSL, or resolve Alexa+ microphone routing and Fire TV screen/power behavior. Those still require Amazon's console or physical-device checks.

## CI and release gates

The same workflow runs on PRs, `master` pushes, version-tag pushes, manual runs and a weekly schedule. Jobs check formatting, Ruff, Actions/shell syntax, SDK and HTTP/TLS tests on Linux Python 3.8/3.13 and Windows Python 3.13, HA/Node-RED examples, both deployment packages, both packaged simulations, and CodeQL for Python and Actions. The SDK job requires at least **85% combined statement/branch coverage**. JUnit, coverage JSON/XML, summaries, CodeQL SARIF and simulation logs are kept as Actions artifacts, including after failures. High/critical CodeQL security findings (security severity >= 7) fail the security job and block release; other findings remain visible in GitHub Security for review. A missing SARIF report also fails the gate.

**CI passed** fails if any dependency fails, is cancelled, or is skipped. Configure that stable check as required in branch protection; existing required checks from the replaced workflows need to be updated. The workflow itself does not change repository protection settings. PR checks use read-only repository permissions; only CodeQL has security-events access and only the tag release job can write release contents.

To publish a future release, update the handler's `# VERSION`, merge the tested change, then push a matching `vX.Y.Z` tag. Every gate reruns on that exact tag. The release job downloads the already-tested ZIPs from that run, verifies the source commit, clean build checkout, handler contents, absence of private `settings.json`, version and SHA-256 against build manifests, then creates a draft with both ZIPs, dependency manifests and `SHA256SUMS`. It publishes only after asset creation succeeds. It refuses to overwrite an existing release; remove an incomplete draft before retrying. Creating a release manually in GitHub bypasses this publishing sequence, so use the tag workflow. Tests for the publication guard explicitly reject wrong versions, tampered ZIPs, wrong commits, dirty builds, missing packages and private settings. No live AWS/HA deployment is configured.
