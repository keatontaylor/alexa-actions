"""Localization and safe diagnostics, independent of HA transport."""

import json
from pathlib import Path

from ask_sdk_core.dispatch_components import AbstractRequestInterceptor, AbstractResponseInterceptor
from utils import get_logger

logger = get_logger(False)


class DiagnosticsInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        envelope = handler_input.request_envelope
        request = envelope.request
        intent = getattr(request, "intent", None)
        system = envelope.context.system if envelope.context else None
        device = system.device if system else None
        supported = device.supported_interfaces if device else None
        interfaces = (
            sorted(
                external
                for field, external in supported.attribute_map.items()
                if getattr(supported, field, None) is not None
            )
            if supported
            else []
        )
        logger.info(
            "request type=%s intent=%s locale=%s id=%s interfaces=%s",
            request.object_type,
            intent.name if intent else None,
            getattr(request, "locale", None),
            request.request_id,
            interfaces,
        )


class ResponseDiagnosticsInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        client = handler_input.attributes_manager.request_attributes.get("ha")
        logger.info(
            "response id=%s end_session=%s ha_state=%s completed=%s",
            handler_input.request_envelope.request.request_id,
            response.should_end_session if response else None,
            type(client.ha_state).__name__ if client else None,
            client.completed if client else False,
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """Add function to request attributes, that can load locale specific data."""

    def process(self, handler_input):
        """Load locale specific data."""
        locale = handler_input.request_envelope.request.locale or "en-US"
        logger.info("Locale is %s", locale)

        # localized strings stored in language_strings.json
        with (Path(__file__).parent / "language_strings.json").open(encoding="utf-8") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        data = {**language_data["en"], **language_data.get(locale[:2], {})}
        # if a more specialized translation exists, then select it instead
        # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
        #          then pick that instead
        if locale in language_data:
            data.update(language_data[locale])
        handler_input.attributes_manager.request_attributes["_"] = data
