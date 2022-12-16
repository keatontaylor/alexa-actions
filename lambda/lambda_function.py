# VERSION 0.8.2

# UPDATE THESE VARIABLES WITH YOUR CONFIG
HOME_ASSISTANT_URL = 'https://yourinstall.com'  # REPLACE WITH THE URL FOR YOUR HOME ASSISTANT
VERIFY_SSL = True  # SET TO FALSE IF YOU DO NOT HAVE VALID CERTS
TOKEN = ''  # ADD YOUR LONG LIVED TOKEN IF NEEDED OTHERWISE LEAVE BLANK
DEBUG = False  # SET TO TRUE IF YOU WANT TO SEE MORE DETAILS IN THE LOGS

""" NO NEED TO EDIT ANYTHING UNDER THE LINE """
import sys
import logging
import urllib3
import json
import isodate
import prompts
from datetime import datetime
from typing import Union, Optional
from urllib3 import HTTPResponse

from ask_sdk_core.utils import (
    get_account_linking_access_token,
    is_request_type,
    is_intent_name,
    get_intent_name,
    get_slot,
    get_slot_value
)
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_model import SessionEndedReason
from ask_sdk_model.slu.entityresolution import StatusCode

HOME_ASSISTANT_URL = HOME_ASSISTANT_URL.rstrip('/')

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

INPUT_TEXT_ENTITY = "input_text.alexa_actionable_notification"

RESPONSE_YES = "ResponseYes"
RESPONSE_NO = "ResponseNo"
RESPONSE_NONE = "ResponseNone"
RESPONSE_SELECT = "ResponseSelect"
RESPONSE_NUMERIC = "ResponseNumeric"
RESPONSE_DURATION = "ResponseDuration"
RESPONSE_STRING = "ResponseString"
RESPONSE_DATE_TIME = "ResponseDateTime"


class Borg:
    """Borg MonoState Class for State Persistence."""
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class HomeAssistant(Borg):
    """HomeAssistant Wrapper Class."""

    def __init__(self, handler_input=None):
        Borg.__init__(self)
        if handler_input:
            self.handler_input = handler_input

        # Gets data from langua_strings.json file according to the locale
        self.language_strings = self.handler_input.attributes_manager.request_attributes["_"]

        self.token = self._fetch_token() if TOKEN == "" else TOKEN

        self.get_ha_state()

    def clear_state(self):
        """
            Clear the state of the local Home Assistant object.
        """

        logger.debug("Clearing Home Assistant local state")
        self.ha_state = None

    def _fetch_token(self):
        logger.debug("Fetching Home Assistant token from Alexa")
        return get_account_linking_access_token(self.handler_input)

    def _check_response_errors(self, response: HTTPResponse) -> Union[bool, str]:
        if response.status == 401:
            logger.error(f'401 Error from Home Assistant. Activate debug mode to see more details.')
            logger.debug(response.data)
            speak_output = "Error 401 " + self.language_strings[prompts.ERROR_401]
            return speak_output
        if response.status == 404:
            logger.error(f'404 Error from Home Assistant. Activate debug mode to see more details.')
            logger.debug(response.data)
            speak_output = "Error 404 " + self.language_strings[prompts.ERROR_404]
            return speak_output
        if response.status >= 400:
            logger.error(f'{response.status} Error from Home Assistant. '
                         f'Activate debug mode to see more details.')
            logger.debug(response.data)
            speak_output = f'Error {response.status}, {self.language_strings[prompts.ERROR_400]}'
            return speak_output

        return False

    def get_ha_state(self) -> None:
        """
            Updates the local Home Assistant state with the
            latest state from the Home Assistant server.
        """

        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=10.0, read=10.0)
        )

        response = http.request(
            'GET',
            f'{HOME_ASSISTANT_URL}/api/states/{INPUT_TEXT_ENTITY}',
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
        )

        errors: Union[bool, str] = self._check_response_errors(response)
        if errors:
            self.ha_state = {
                "error": True,
                "text": errors
            }
            logger.debug(self.ha_state)
            return

        decoded_response: Union[str, bytes] = json.loads(response.data.decode('utf-8')).get('state')
        if not decoded_response:
            logger.error("No entity state provided by Home Assistant. "
                         "Did you forget to add the actionable notification entity?")
            self.ha_state = {
                "error": True,
                "text": self.language_strings[prompts.ERROR_CONFIG]
            }
            logger.debug(self.ha_state)
            return

        self.ha_state = {
            "error": False,
            "event_id": json.loads(decoded_response).get('event'),
            "text": json.loads(decoded_response).get('text')
        }
        logger.debug(self.ha_state)

    def post_ha_event(self, response: str, response_type: str, **kwargs) -> str:
        """
            Posts an event to the Home Assistant server.

            :param response: The response to send to the Home Assistant server.
            :param response_type: The type of response to send to the Home Assistant server.
            :param kwargs: Additional parameters to send to the Home Assistant server.
            :return: The text to speak to the user.
        """

        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=10.0, read=10.0)
        )

        request_body = {
            "event_id": self.ha_state.get('event_id'),
            "event_response": response,
            "event_response_type": response_type
        }
        request_body.update(kwargs)

        if self.handler_input.request_envelope.context.system.person:
            person_id = self.handler_input.request_envelope.context.system.person.person_id
            request_body['event_person_id'] = person_id

        response = http.request(
            'POST',
            f'{HOME_ASSISTANT_URL}/api/events/alexa_actionable_notification',
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            body=json.dumps(request_body).encode('utf-8')
        )

        error: Union[bool, str] = self._check_response_errors(response)
        if error:
            return error

        speak_output: str = self.language_strings[prompts.OKAY]
        self.clear_state()
        return speak_output

    def get_value_for_slot(self, slot_name):
        """"Get value from slot, also known as the (why does amazon make you do this)"""
        slot = get_slot(self.handler_input, slot_name=slot_name)
        if slot and slot.resolutions and slot.resolutions.resolutions_per_authority:
            for resolution in slot.resolutions.resolutions_per_authority:
                if resolution.status.code == StatusCode.ER_SUCCESS_MATCH:
                    for value in resolution.values:
                        if value.value and value.value.name:
                            return value.value.name


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        """Check for Launch Request."""
        return is_request_type('LaunchRequest')(handler_input)

    def handle(self, handler_input):
        """Handler for Skill Launch."""
        ha_obj = HomeAssistant(handler_input)
        speak_output: Optional[str] = ha_obj.ha_state['text']
        event_id: Optional[str] = ha_obj.ha_state['event_id']

        if event_id:
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask('')
                    .response
            )
        else:
            ha_obj.clear_state()
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
            )


class YesIntentHanlder(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        """Check for Yes Intent."""
        return is_intent_name('AMAZON.YesIntent')(handler_input)

    def handle(self, handler_input):
        """Handle Yes Intent."""
        logger.info('Yes Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_YES, RESPONSE_YES)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class NoIntentHanlder(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        """Check for No Intent."""
        return is_intent_name('AMAZON.NoIntent')(handler_input)

    def handle(self, handler_input):
        """Handle No Intent."""
        logger.info('No Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        speak_output = ha_obj.post_ha_event(RESPONSE_NO, RESPONSE_NO)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class NumericIntentHandler(AbstractRequestHandler):
    """Handler for Select Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name('Number')(handler_input)

    def handle(self, handler_input):
        """Handle the Select intent."""
        logger.info('Numeric Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        number = get_slot_value(handler_input, 'Numbers')
        logger.debug(f'Number: {number}')
        if number == '?':
            raise
        speak_output = ha_obj.post_ha_event(number, RESPONSE_NUMERIC)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class StringIntentHandler(AbstractRequestHandler):
    """Handler for String Intent."""
    
    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name('String')(handler_input)

    def handle(self, handler_input):
        """Handle String Intent."""
        logger.info('String Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        strings = get_slot_value(handler_input, 'Strings')
        logger.debug(f'String: {strings}')

        speak_output = ha_obj.post_ha_event(strings, RESPONSE_STRING)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SelectIntentHandler(AbstractRequestHandler):
    """Handler for Select Intent."""

    def can_handle(self, handler_input):
        """Check for Select Intent."""
        return is_intent_name('Select')(handler_input)

    def handle(self, handler_input):
        """Handle Select Intent."""
        logger.info('Selection Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        selection = ha_obj.get_value_for_slot('Selections')
        logger.debug(f'Selection: {selection}')

        if not selection:
            raise

        ha_obj.post_ha_event(selection, RESPONSE_SELECT)
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.SELECTED].format(selection)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class DurationIntentHandler(AbstractRequestHandler):
    """Handler for Duration Intent."""

    def can_handle(self, handler_input):
        """Check for Duration Intent."""
        return is_intent_name('Duration')(handler_input)

    def handle(self, handler_input):
        """Handle the Duration Intent."""
        logger.info('Duration Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        duration = get_slot_value(handler_input, 'Durations')

        logger.debug(f'Duration: {duration}')

        speak_output = ha_obj.post_ha_event(
            isodate.parse_duration(duration).total_seconds(), RESPONSE_DURATION)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class DateTimeIntentHandler(AbstractRequestHandler):
    """Handler for Date Time Intent."""

    def can_handle(self, handler_input):
        """Check for Date Time Intent."""
        return is_intent_name('Date')(handler_input)

    def handle(self, handler_input):
        """Handle the Date Time intent."""
        logger.info('Date Intent Handler triggered')
        ha_obj = HomeAssistant(handler_input)

        date = get_slot_value(handler_input, 'Dates')
        time = get_slot_value(handler_input, 'Times')

        logger.debug(f'Dates: {date} of type {type(date)}')
        logger.debug(f'Times: {time} of type {type(time)}')

        if not date and not time:
            raise

        speak_output = ha_obj.post_ha_event(json.dumps({
            **self._parse_date(date),
            **self._parse_time(time)
        }), RESPONSE_DATE_TIME)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )

    @staticmethod
    def _parse_date(date: str) -> dict:
        date_data = {
            'day': None,
            'month': None,
            'year': None,
        }

        if not date:
            return date_data

        date = date.split('-')
        date_len = len(date)

        date_data['day'] = date[2] if date_len >= 3 else None
        date_data['month'] = date[1] if date_len >= 2 else None
        date_data['year'] = date[0] if date_len >= 1 else None

        return date_data

    @staticmethod
    def _parse_time(time: str) -> dict:
        time_data = {
            'seconds': None,
            'minute': None,
            'hour': None,
        }

        if not time:
            return time_data

        # If the letter s is present then the hole time represents a second
        if 's' in time.lower():
            time_data['seconds'] = time.lower().replace('s', '')
            return time_data
        if 'm' in time.lower():
            time_data['minute'] = time.lower().replace('m', '')
            return time_data
        if 'h' in time.lower():
            time_data['hour'] = time.lower().replace('h', '')
            return time_data

        time = time.split(':')
        time_len = len(time)

        time_data['seconds'] = time[2] if time_len >= 3 else None
        time_data['minute'] = time[1] if time_len >= 2 else None
        time_data['hour'] = time[0] if time_len >= 1 else None

        return time_data


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        """Check for Cancel and Stop Intent."""
        return (is_intent_name('AMAZON.CancelIntent')(handler_input) or
                is_intent_name('AMAZON.StopIntent')(handler_input))

    def handle(self, handler_input):
        """Handle Cancel and Stop Intent."""
        logger.info('Cancel or Stop Intent Handler triggered')
        data = handler_input.attributes_manager.request_attributes["_"]
        speak_output = data[prompts.STOP_MESSAGE]

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        """Check for Session End."""
        return is_request_type('SessionEndedRequest')(handler_input)

    def handle(self, handler_input):
        """Clean up and stop the skill."""
        logger.info('Session Ended Request Handler triggered')
        ha_obj = HomeAssistant(handler_input)
        reason = handler_input.request_envelope.request.reason
        if reason == SessionEndedReason.EXCEEDED_MAX_REPROMPTS or reason == SessionEndedReason.USER_INITIATED:
            ha_obj.post_ha_event(RESPONSE_NONE, RESPONSE_NONE)

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        """Check if can handle IntentReflectorHandler."""
        return is_request_type('IntentRequest')(handler_input)

    def handle(self, handler_input):
        """Simulate an intent."""
        logger.info('Reflector Intent triggered')
        intent_name = get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


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
        logger.info('Catch All Exception triggered')
        logger.error(exception, exc_info=True)
        ha_obj = HomeAssistant()

        data = handler_input.attributes_manager.request_attributes["_"]
        if ha_obj.ha_state and ha_obj.ha_state.get('text'):
            speak_output = data[prompts.ERROR_ACOUSTIC].format(ha_obj.ha_state.get('text'))
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask('')
                    .response
            )
        speak_output = data[prompts.ERROR_CONFIG].format(ha_obj.ha_state.get('text'))
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """Add function to request attributes, that can load locale specific data."""

    def process(self, handler_input):
        """Load locale specific data."""
        locale = handler_input.request_envelope.request.locale
        logger.info(f'Locale is {locale[:2]}')

        # localized strings stored in language_strings.json
        with open('language_strings.json', encoding='utf-8') as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        data = language_data[locale[:2]]
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
sb.add_request_handler(YesIntentHanlder())
sb.add_request_handler(NoIntentHanlder())
sb.add_request_handler(StringIntentHandler())
sb.add_request_handler(SelectIntentHandler())
sb.add_request_handler(NumericIntentHandler())
sb.add_request_handler(DurationIntentHandler())
sb.add_request_handler(DateTimeIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler())

# register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# register response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
