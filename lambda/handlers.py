"""Alexa request routing; HA access is injected by the skill entrypoint."""

import json
from typing import Optional

import isodate
from ask_sdk_core.dispatch_components import AbstractExceptionHandler, AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_intent_name, get_slot, get_simple_slot_values
from ask_sdk_model import SessionEndedReason

import prompts
from schemas import HaState, HaStateError
from const import (
    RESPONSE_YES,
    RESPONSE_NO,
    RESPONSE_NONE,
    RESPONSE_SELECT,
    RESPONSE_NUMERIC,
    RESPONSE_DURATION,
    RESPONSE_STRING,
    RESPONSE_DATE_TIME,
)
from utils import get_logger
from home_assistant import SESSION_KEY, COMPLETED_KEY

logger = get_logger(False)


class ClientHandler:
    def __init__(self, client_factory):
        self.client_factory = client_factory


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


def _slot_value(handler_input, name):
    slot = get_slot(handler_input, name)
    if slot is None:
        return None
    if slot.slot_value is not None:
        values = get_simple_slot_values(slot.slot_value)
        return values[0].value if len(values) == 1 else None
    return slot.value


class LaunchRequestHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        """Check for Launch Request."""
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """Handler for Skill Launch."""
        ha_obj = self.client_factory(handler_input)
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


class YesIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        """Check for Yes Intent."""
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        """Handle Yes Intent."""
        logger.info("Yes Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_YES, RESPONSE_YES)

        return _handle_response(handler_input, speak_output)


class NoIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        """Check for No Intent."""
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        """Handle No Intent."""
        logger.info("No Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_NO, RESPONSE_NO)

        return _handle_response(handler_input, speak_output)


class NumericIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Select Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("Number")(handler_input)

    def handle(self, handler_input):
        """Handle the Select intent."""
        logger.info("Numeric Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)
        number = _slot_value(handler_input, "Numbers")
        logger.debug(f"Number: {number}")
        if not number or number == "?":
            raise ValueError("Number slot is missing or unresolved")
        speak_output = ha_obj.post_ha_event(number, RESPONSE_NUMERIC)

        return _handle_response(handler_input, speak_output)


class CommandIntentHandler(ClientHandler, AbstractRequestHandler):
    def can_handle(self, handler_input):
        if is_intent_name("Command")(handler_input):
            return True
        attributes = handler_input.attributes_manager.session_attributes
        session = handler_input.request_envelope.session
        return (
            session is not None
            and session.new
            and not attributes.get(SESSION_KEY)
            and not attributes.get(COMPLETED_KEY)
            and any(is_intent_name(name)(handler_input) for name in ("String", "FreeText"))
        )

    def handle(self, handler_input):
        client = self.client_factory(handler_input)
        text = (
            _slot_value(handler_input, "CommandText")
            or _slot_value(handler_input, "FreeTextValue")
            or _slot_value(handler_input, "Strings")
        )
        if not text:
            return _handle_response(handler_input, "Please give a command after the command phrase.")
        if isinstance(client.ha_state, HaState) and not client.completed:
            return handler_input.response_builder.speak(client.ha_state.text).ask("").response
        return _handle_response(handler_input, client.post_command(text, get_intent_name(handler_input)))


class StringIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for String Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("String")(handler_input) or is_intent_name("FreeText")(handler_input)

    def handle(self, handler_input):
        """Handle String Intent."""
        logger.info("String Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)
        strings = _slot_value(handler_input, "FreeTextValue") or _slot_value(handler_input, "Strings")
        logger.debug("String intent received")
        if not strings:
            raise ValueError("String slot is missing")

        speak_output = ha_obj.post_ha_event(strings, RESPONSE_STRING)

        return _handle_response(handler_input, speak_output)


class SelectIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Select Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("Select")(handler_input)

    def handle(self, handler_input):
        """Handle Select Intent."""
        logger.info("Selection Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)
        selection = ha_obj.get_value_for_slot("Selections")
        logger.debug(f"Selection: {selection}")

        if not selection:
            raise ValueError("Selection slot is missing or unresolved")

        speak_output = ha_obj.post_ha_event(selection, RESPONSE_SELECT)
        if ha_obj.completed and speak_output:
            speak_output = ha_obj.language_strings[prompts.SELECTED].format(selection)

        return _handle_response(handler_input, speak_output)


class DurationIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Duration Intent."""

    def can_handle(self, handler_input):
        """Check for Duration Intent."""
        return is_intent_name("Duration")(handler_input)

    def handle(self, handler_input):
        """Handle the Duration Intent."""
        logger.info("Duration Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)
        duration = _slot_value(handler_input, "Durations")

        logger.debug(f"Duration: {duration}")

        if not duration:
            raise ValueError("Duration slot is missing")
        speak_output = ha_obj.post_ha_event(isodate.parse_duration(duration).total_seconds(), RESPONSE_DURATION)

        return _handle_response(handler_input, speak_output)


class DateTimeIntentHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Date Time Intent."""

    def can_handle(self, handler_input):
        """Check for Date Time Intent."""
        return is_intent_name("Date")(handler_input)

    def handle(self, handler_input):
        """Handle the Date Time intent."""
        logger.info("Date Intent Handler triggered")
        ha_obj = self.client_factory(handler_input)

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


class CancelOrStopIntentHandler(ClientHandler, AbstractRequestHandler):
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
        ha_obj = self.client_factory(handler_input)
        ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = ha_obj.ha_state.text if isinstance(ha_obj.ha_state, HaStateError) else data[prompts.STOP_MESSAGE]

        return _handle_response(handler_input, speak_output)


class FallbackHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Fallback."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        """Handle Fallback."""
        logger.info("Fallback Handler triggered")
        ha_obj = self.client_factory(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)
        return _handle_response(handler_input, speak_output)


class SessionEndedRequestHandler(ClientHandler, AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        """Check for Session End."""
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        """Clean up and stop the skill."""
        logger.info("Session Ended Request Handler triggered")
        ha_obj = self.client_factory(handler_input)
        reason = handler_input.request_envelope.request.reason
        if reason == SessionEndedReason.EXCEEDED_MAX_REPROMPTS or reason == SessionEndedReason.USER_INITIATED:
            ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)

        return handler_input.response_builder.response


class HelpIntentHandler(ClientHandler, AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        ha_obj = self.client_factory(handler_input)
        speech = ha_obj.language_strings[prompts.HELP_MESSAGE]
        if isinstance(ha_obj.ha_state, HaState) and ha_obj.ha_state.event_id and not ha_obj.completed:
            return handler_input.response_builder.speak(speech + " " + ha_obj.ha_state.text).ask("").response
        return _handle_response(handler_input, speech)


class IntentReflectorHandler(ClientHandler, AbstractRequestHandler):
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
