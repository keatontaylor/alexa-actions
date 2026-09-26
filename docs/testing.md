# Testing without an Echo

The local suite uses the real Amazon ASK SDK and request envelopes, with a fake Home Assistant HTTP boundary. It does not require an Alexa device, Amazon credentials, a Home Assistant token, or access to a live home.

```sh
python -m venv .venv
# Activate the environment for your OS.
python -m pip install -r requirements-test.txt
python -m pytest tests
python scripts/build_package.py --kind pure
python scripts/check_package.py dist/AlexaActionsNoBinaryLinux.zip
```

Each PR builds both ZIPs on Linux with Python 3.13 and tests the extracted ZIP with site packages disabled. Download its artifacts from the **Build Linux** run. The binary artifact targets self-managed Lambda Python 3.13 / x86_64. The pure artifact contains no native extensions. All dependencies, including the ASK SDK, are installed into the package; uploading only `lambda_function.py` is insufficient.

For a self-managed AWS Lambda, upload the ZIP directly and set the handler to `lambda_function.lambda_handler`. Its files are at the ZIP root, per the [AWS Python deployment guide](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html). Use a currently supported runtime from [AWS's runtime table](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html); Python 3.13 is the runtime tested here. A binary package for another Python version or architecture must be rebuilt for that target.

For **Alexa-hosted** skills, use the source files and `requirements.txt` in the console's `lambda` folder. Amazon runs pip during the hosted build. Alexa controls the hosted runtime; changing a self-managed Lambda setting is not a hosted-runtime upgrade procedure. See [Create and manage Alexa-hosted skills](https://developer.amazon.com/en-US/docs/alexa/hosted-skills/alexa-hosted-skills-create.html). The project uses [ASK SDK core](https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/set-up-the-sdk.html) without its optional DynamoDB adapter.

The [Alexa simulator](https://developer.amazon.com/en-US/docs/alexa/devconsole/alexa-simulator.html) can test speech/text, routing, session attributes, and backend requests without a device. Import and build the complete interaction model for the selected locale, enable development testing, deploy the backend, and inspect **Skill I/O**. With a test HA helper, launch the skill and try Yes, No, a number, a duration, a selection, Stop, and silence. Also change the helper while an earlier question is open and check that its response retains its original event ID.

The simulator and local tests cannot establish Fire TV power behavior, far-field recognition with background noise, device-specific microphone/screen timing, or whether every physical device sends `SessionEndedRequest`. Those require reports from device owners. No physical-device validation is claimed by a passing local suite.

Official documentation checked on 2026-09-26. Software checks do not prove an Alexa-hosted deployment or live event delivery.
