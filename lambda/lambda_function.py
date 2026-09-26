# VERSION 0.12.0

# UPDATE THESE VARIABLES WITH YOUR CONFIG
HOME_ASSISTANT_URL = "https://yourinstall.com"  # REPLACE WITH THE URL FOR YOUR HOME ASSISTANT
VERIFY_SSL = True  # SET TO FALSE IF YOU DO NOT HAVE VALID CERTS
TOKEN = ""  # ADD YOUR LONG LIVED TOKEN IF NEEDED OTHERWISE LEAVE BLANK
INCLUDE_DEVICE_ID = False  # OPTIONAL: ADD AMAZON DEVICE ID TO RESPONSE EVENTS
DEBUG = False  # SET TO TRUE IF YOU WANT TO SEE MORE DETAILS IN THE LOGS

""" NO NEED TO EDIT ANYTHING UNDER THE LINE """
# Built-In Imports
import json
from pathlib import Path
from typing import Optional

# 3rd-Party Imports
import isodate
import urllib3
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import (
    get_account_linking_access_token,
    is_request_type,
    is_intent_name,
    get_intent_name,
    get_slot,
    get_simple_slot_values,
)
from ask_sdk_model import SessionEndedReason
from ask_sdk_model.slu.entityresolution import StatusCode

# Local Imports
import prompts
from pydantic import ValidationError
from schemas import HaState, HaStateError
from utils import get_logger
from const import (
    INPUT_TEXT_ENTITY,
    RESPONSE_YES,
    RESPONSE_NO,
    RESPONSE_NONE,
    RESPONSE_SELECT,
    RESPONSE_NUMERIC,
    RESPONSE_DURATION,
    RESPONSE_STRING,
    RESPONSE_DATE_TIME,
)

HOME_ASSISTANT_URL = HOME_ASSISTANT_URL.rstrip("/")

logger = get_logger(DEBUG)


def _handle_response(handler, speak_out: Optional[str]):
    """
    This function has the purpose of allowing the suspension of the default Okay response
    so the user can have home assistant do a custom response or follow-up question.

    Fixed issue: #147

    :param handler:
    :param speak_out:
    :return:
    """
    builder = handler.response_builder.set_should_end_session(True)
    if speak_out:
        builder.speak(speak_out)
    return builder.response


SESSION_KEY = "alexa_actionable_notification"
COMPLETED_KEY = "alexa_actionable_notification_completed"


def _init_http_pool():
    # A failed HA connection must fit within Alexa's request-response deadline.
    return urllib3.PoolManager(
        cert_reqs="CERT_REQUIRED" if VERIFY_SSL else "CERT_NONE",
        timeout=urllib3.Timeout(total=3.0, connect=1.0, read=2.0),
        retries=False,
    )


def _string_to_bool(value: Optional[str], default: bool = False) -> bool:
    """
    Used because we need to convert boolean values passed in strings since
    entity states don't natively support json and are treated as strings.

    :param value:
    :param default:
    :return:
    """
    if isinstance(value, bool):
        return value

    if not isinstance(value, str):
        return default

    value = value.lower()
    if value == "true":
        return True
    elif value == "false":
        return False

    return default


def _slot_value(handler_input, name):
    slot = get_slot(handler_input, name)
    if slot is None:
        return None
    if slot.slot_value is not None:
        values = get_simple_slot_values(slot.slot_value)
        return values[0].value if len(values) == 1 else None
    return slot.value


class HomeAssistant:
    """One request's HA client, with notification context carried by Alexa's session."""

    def __init__(self, handler_input):
        self.handler_input = handler_input
        self.ha_state = None
        self.http = _init_http_pool()
        attributes = handler_input.attributes_manager
        attributes.request_attributes["ha"] = self
        self.language_strings = attributes.request_attributes["_"]
        self.session = attributes.session_attributes
        self.token = TOKEN or get_account_linking_access_token(handler_input)
        self.completed = bool(self.session.get(COMPLETED_KEY, False))
        if is_request_type("LaunchRequest")(handler_input):
            self.session.pop(SESSION_KEY, None)
            self.session[COMPLETED_KEY] = False
            self.completed = False
            self.get_ha_state()
            if isinstance(self.ha_state, HaState):
                self.session[SESSION_KEY] = self.ha_state.dict()
        else:
            # Never re-read a mutable helper to resolve an answer or an old end callback.
            snapshot = self.session.get(SESSION_KEY)
            try:
                self.ha_state = HaState.parse_obj(snapshot) if isinstance(snapshot, dict) else None
            except ValidationError:
                self._set_ha_error(prompts.ERROR_CONFIG)

    def _set_ha_error(self, prompt):
        self.ha_state = HaStateError(text=self.language_strings[prompt])

    @staticmethod
    def _build_url(*path):
        return f"{HOME_ASSISTANT_URL.rstrip('/')}/" + "/".join(path)

    def _get_headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def _request(self, method, *path, body=None, extra_headers=None):
        if not self.token:
            self._set_ha_error(prompts.ERROR_401)
            return None
        headers = self._get_headers()
        if extra_headers:
            headers.update(extra_headers)
        try:
            response = self.http.request(
                method,
                self._build_url(*path),
                headers=headers,
                **({"body": json.dumps(body).encode("utf-8")} if body is not None else {}),
            )
        except (urllib3.exceptions.HTTPError, OSError):
            logger.warning("HA transport failed for %s %s", method, "/".join(path))
            self._set_ha_error(prompts.ERROR_400)
            return None
        logger.info("HA %s %s status=%s", method, "/".join(path), response.status)
        if response.status >= 300:
            prompt = {401: prompts.ERROR_401, 404: prompts.ERROR_404}.get(response.status, prompts.ERROR_400)
            self.ha_state = HaStateError(text=f"Error {response.status} " + self.language_strings[prompt])
            return None
        return response

    def _get(self, *path, extra_headers=None):
        return self._request("GET", *path, extra_headers=extra_headers)

    def _post(self, *path, body, extra_headers=None):
        return self._request("POST", *path, body=body, extra_headers=extra_headers)

    def get_ha_state(self):
        response = self._get("api", "states", INPUT_TEXT_ENTITY)
        if response is None:
            return
        try:
            outer = json.loads(response.data.decode("utf-8"))
            state = json.loads(outer["state"])
            if not isinstance(state, dict) or not isinstance(state.get("text"), str) or not state["text"]:
                raise ValueError("Missing notification text")
            event = state.get("event")
            request_id = state.get("request_id")
            if event is not None and not isinstance(event, str):
                raise ValueError("Invalid event ID")
            if request_id is not None and not isinstance(request_id, str):
                raise ValueError("Invalid request ID")
            self.ha_state = HaState(
                event_id=event,
                text=state["text"],
                request_id=request_id,
                suppress_confirmation=_string_to_bool(state.get("suppress_confirmation")),
            )
        except (ValueError, TypeError, KeyError, AttributeError, ValidationError):
            logger.warning("HA helper does not contain a valid notification object")
            self._set_ha_error(prompts.ERROR_CONFIG)

    def post_ha_event(self, response, response_type, **kwargs):
        if self.completed:
            return ""
        if not isinstance(self.ha_state, HaState) or not self.ha_state.event_id:
            if not isinstance(self.ha_state, HaStateError):
                self._set_ha_error(prompts.ERROR_CONFIG)
            return self.ha_state.text
        state = self.ha_state
        body = {"event_id": state.event_id, "event_response": response, "event_response_type": response_type}
        if state.request_id:
            body["request_id"] = state.request_id
        body.update(kwargs)
        system = self.handler_input.request_envelope.context.system
        if system.person and system.person.person_id:
            body["event_person_id"] = system.person.person_id
        if INCLUDE_DEVICE_ID and system.device and system.device.device_id:
            body["event_device_id"] = system.device.device_id
        if self._post("api", "events", "alexa_actionable_notification", body=body) is None:
            return self.ha_state.text
        self.completed = True
        self.session[COMPLETED_KEY] = True
        return "" if state.suppress_confirmation else self.language_strings[prompts.OKAY]

    def get_value_for_slot(self, slot_name):
        slot = get_slot(self.handler_input, slot_name=slot_name)
        if slot and slot.resolutions and slot.resolutions.resolutions_per_authority:
            for resolution in slot.resolutions.resolutions_per_authority:
                if resolution.status.code == StatusCode.ER_SUCCESS_MATCH:
                    for value in resolution.values or []:
                        if value.value and value.value.name:
                            return value.value.name
        return None


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        """Check for Launch Request."""
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """Handler for Skill Launch."""
        ha_obj = HomeAssistant(handler_input)
        state = ha_obj.ha_state
        if not isinstance(state, HaState):
            return _handle_response(
                handler_input, state.text if state else ha_obj.language_strings[prompts.ERROR_CONFIG]
            )
        handler = handler_input.response_builder.speak(state.text)
        if state.event_id:
            handler.ask("")
        else:
            handler.set_should_end_session(True)
        return handler.response


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        """Check for Yes Intent."""
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        """Handle Yes Intent."""
        logger.info("Yes Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_YES, RESPONSE_YES)

        return _handle_response(handler_input, speak_output)


class NoIntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        """Check for No Intent."""
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        """Handle No Intent."""
        logger.info("No Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_NO, RESPONSE_NO)

        return _handle_response(handler_input, speak_output)


class NumericIntentHandler(AbstractRequestHandler):
    """Handler for Select Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("Number")(handler_input)

    def handle(self, handler_input):
        """Handle the Select intent."""
        logger.info("Numeric Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        number = _slot_value(handler_input, "Numbers")
        logger.debug(f"Number: {number}")
        if not number or number == "?":
            raise ValueError("Number slot is missing or unresolved")
        speak_output = ha_obj.post_ha_event(number, RESPONSE_NUMERIC)

        return _handle_response(handler_input, speak_output)


class StringIntentHandler(AbstractRequestHandler):
    """Handler for String Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("String")(handler_input) or is_intent_name("FreeText")(handler_input)

    def handle(self, handler_input):
        """Handle String Intent."""
        logger.info("String Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        strings = _slot_value(handler_input, "FreeText") or _slot_value(handler_input, "Strings")
        logger.debug("String intent received")
        if not strings:
            raise ValueError("String slot is missing")

        speak_output = ha_obj.post_ha_event(strings, RESPONSE_STRING)

        return _handle_response(handler_input, speak_output)


class SelectIntentHandler(AbstractRequestHandler):
    """Handler for Select Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("Select")(handler_input)

    def handle(self, handler_input):
        """Handle Select Intent."""
        logger.info("Selection Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        selection = ha_obj.get_value_for_slot("Selections")
        logger.debug(f"Selection: {selection}")

        if not selection:
            raise ValueError("Selection slot is missing or unresolved")

        speak_output = ha_obj.post_ha_event(selection, RESPONSE_SELECT)
        if ha_obj.completed and speak_output:
            speak_output = ha_obj.language_strings[prompts.SELECTED].format(selection)

        return _handle_response(handler_input, speak_output)


class DurationIntentHandler(AbstractRequestHandler):
    """Handler for Duration Intent."""

    def can_handle(self, handler_input):
        """Check for Duration Intent."""
        return is_intent_name("Duration")(handler_input)

    def handle(self, handler_input):
        """Handle the Duration Intent."""
        logger.info("Duration Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        duration = _slot_value(handler_input, "Durations")

        logger.debug(f"Duration: {duration}")

        if not duration:
            raise ValueError("Duration slot is missing")
        speak_output = ha_obj.post_ha_event(isodate.parse_duration(duration).total_seconds(), RESPONSE_DURATION)

        return _handle_response(handler_input, speak_output)


class DateTimeIntentHandler(AbstractRequestHandler):
    """Handler for Date Time Intent."""

    def can_handle(self, handler_input):
        """Check for Date Time Intent."""
        return is_intent_name("Date")(handler_input)

    def handle(self, handler_input):
        """Handle the Date Time intent."""
        logger.info("Date Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)

        date = _slot_value(handler_input, "Dates")
        time = _slot_value(handler_input, "Times")

        logger.debug(f"Dates: {date} of type {type(date)}")
        logger.debug(f"Times: {time} of type {type(time)}")

        if not date and not time:
            raise ValueError("Date and time slots are missing")

        speak_output = ha_obj.post_ha_event(
            json.dumps({**self._parse_date(date), **self._parse_time(time)}), RESPONSE_DATE_TIME
        )

        return _handle_response(handler_input, speak_output)

    @staticmethod
    def _parse_date(date: str) -> dict:
        date_data = {
            "day": None,
            "month": None,
            "year": None,
        }

        if not date:
            return date_data

        date = date.split("-")
        date_len = len(date)

        date_data["day"] = date[2] if date_len >= 3 else None
        date_data["month"] = date[1] if date_len >= 2 else None
        date_data["year"] = date[0] if date_len >= 1 else None

        return date_data

    @staticmethod
    def _parse_time(time: str) -> dict:
        time_data = {
            "seconds": None,
            "minute": None,
            "hour": None,
        }

        if not time:
            return time_data

        # If the letter s is present then the hole time represents a second
        if "s" in time.lower():
            time_data["seconds"] = time.lower().replace("s", "")
            return time_data
        if "m" in time.lower():
            time_data["minute"] = time.lower().replace("m", "")
            return time_data
        if "h" in time.lower():
            time_data["hour"] = time.lower().replace("h", "")
            return time_data

        time = time.split(":")
        time_len = len(time)

        time_data["seconds"] = time[2] if time_len >= 3 else None
        time_data["minute"] = time[1] if time_len >= 2 else None
        time_data["hour"] = time[0] if time_len >= 1 else None

        return time_data


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        """Check for Cancel and Stop Intent."""
        return any(
            is_intent_name(name)(handler_input)
            for name in ("AMAZON.CancelIntent", "AMAZON.StopIntent", "AMAZON.NavigateHomeIntent")
        )

    def handle(self, handler_input):
        """Handle Cancel and Stop Intent."""
        logger.info("Cancel or Stop Intent Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = ha_obj.ha_state.text if isinstance(ha_obj.ha_state, HaStateError) else data[prompts.STOP_MESSAGE]

        return _handle_response(handler_input, speak_output)


class FallbackHandler(AbstractRequestHandler):
    """Handler for Fallback."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        """Handle Fallback."""
        logger.info("Fallback Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)
        return _handle_response(handler_input, speak_output)


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        """Check for Session End."""
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        """Clean up and stop the skill."""
        logger.info("Session Ended Request Handler triggered")
        ha_obj = HomeAssistant(handler_input)
        reason = handler_input.request_envelope.request.reason
        if reason == SessionEndedReason.EXCEEDED_MAX_REPROMPTS or reason == SessionEndedReason.USER_INITIATED:
            ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)

        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        ha_obj = HomeAssistant(handler_input)
        speech = ha_obj.language_strings[prompts.HELP_MESSAGE]
        if isinstance(ha_obj.ha_state, HaState) and ha_obj.ha_state.event_id and not ha_obj.completed:
            return handler_input.response_builder.speak(speech + " " + ha_obj.ha_state.text).ask("").response
        return _handle_response(handler_input, speech)


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        """Check if can handle IntentReflectorHandler."""
        return is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        """Simulate an intent."""
        logger.info("Reflector Intent triggered")
        intent_name = get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return handler_input.response_builder.speak(speak_output).response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """
    Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        """Check if can handle exception."""
        return True

    def handle(self, handler_input, exception):
        """Handle exception."""
        logger.info("Catch All Exception triggered")
        logger.error(exception, exc_info=True)
        # Do not make another network call from error handling.
        attributes = handler_input.attributes_manager.request_attributes
        data = attributes.get("_", {prompts.ERROR_CONFIG: "Please check the skill configuration."})
        ha_obj = attributes.get("ha")
        state = ha_obj.ha_state if ha_obj else None
        if is_request_type("SessionEndedRequest")(handler_input):
            return handler_input.response_builder.response
        if isinstance(state, HaStateError):
            return _handle_response(handler_input, state.text)
        if isinstance(state, HaState) and state.event_id and not ha_obj.completed:
            speech = data[prompts.ERROR_ACOUSTIC].format(state.text)
            return handler_input.response_builder.speak(speech).ask("").response
        return _handle_response(handler_input, data[prompts.ERROR_CONFIG])


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


""" 
    The SkillBuilder object acts as the entry point for your skill, routing all request and response
    payloads to the handlers above. Make sure any new handlers or interceptors you've
    defined are included below. 
    The order matters - they're processed top to bottom.
"""

sb = SkillBuilder()

# register request / intent handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(StringIntentHandler())
sb.add_request_handler(SelectIntentHandler())
sb.add_request_handler(NumericIntentHandler())
sb.add_request_handler(DurationIntentHandler())
sb.add_request_handler(DateTimeIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(IntentReflectorHandler())

# register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# register response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
