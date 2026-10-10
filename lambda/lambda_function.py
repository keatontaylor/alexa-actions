# VERSION 0.13.0

# UPDATE THESE VARIABLES WITH YOUR CONFIG
HOME_ASSISTANT_URL = "https://yourinstall.com"  # REPLACE WITH THE URL FOR YOUR HOME ASSISTANT
VERIFY_SSL = True  # SET TO FALSE IF YOU DO NOT HAVE VALID CERTS
TOKEN = ""  # ADD YOUR LONG LIVED TOKEN IF NEEDED OTHERWISE LEAVE BLANK
INCLUDE_DEVICE_ID = False  # OPTIONAL: ADD AMAZON DEVICE ID TO RESPONSE EVENTS
DEBUG = False  # SET TO TRUE IF YOU WANT TO SEE MORE DETAILS IN THE LOGS


"""Keep deployed constants above; optional file and environment settings override them."""
from pathlib import Path

import urllib3
from ask_sdk_core.skill_builder import SkillBuilder

from configuration import Settings, load_settings
from home_assistant import HomeAssistantClient, SESSION_KEY as SESSION_KEY, COMPLETED_KEY as COMPLETED_KEY
from interceptors import DiagnosticsInterceptor, ResponseDiagnosticsInterceptor, LocalizationInterceptor
from schemas import HaState as HaState, HaStateError as HaStateError
from utils import get_logger
from handlers import (
    LaunchRequestHandler,
    YesIntentHandler,
    NoIntentHandler,
    StringIntentHandler,
    SelectIntentHandler,
    NumericIntentHandler,
    DurationIntentHandler,
    DateTimeIntentHandler,
    CancelOrStopIntentHandler,
    FallbackHandler,
    SessionEndedRequestHandler,
    HelpIntentHandler,
    IntentReflectorHandler,
    CatchAllExceptionHandler,
    CommandIntentHandler,
)

ENABLE_COMMANDS = False
_settings = load_settings({name: globals()[name] for name in Settings.__dataclass_fields__}, Path(__file__).parent)
for _name, _value in vars(_settings).items():
    globals()[_name] = _value
logger = get_logger(DEBUG)


def _init_http_pool():
    # A failed HA connection must fit within Alexa's request-response deadline.
    return urllib3.PoolManager(
        cert_reqs="CERT_REQUIRED" if VERIFY_SSL else "CERT_NONE",
        timeout=urllib3.Timeout(total=3.0, connect=1.0, read=2.0),
        retries=False,
    )


class HomeAssistant(HomeAssistantClient):
    """Supply current runtime settings and the replaceable HTTP factory."""

    def __init__(self, handler_input):
        settings = Settings(**{name: globals()[name] for name in Settings.__dataclass_fields__})
        super().__init__(handler_input, settings, _init_http_pool())


sb = SkillBuilder()
for handler in (
    LaunchRequestHandler,
    YesIntentHandler,
    NoIntentHandler,
    CommandIntentHandler,
    StringIntentHandler,
    SelectIntentHandler,
    NumericIntentHandler,
    DurationIntentHandler,
    DateTimeIntentHandler,
    CancelOrStopIntentHandler,
    FallbackHandler,
    SessionEndedRequestHandler,
    HelpIntentHandler,
    IntentReflectorHandler,
):
    sb.add_request_handler(handler(HomeAssistant))
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_global_request_interceptor(DiagnosticsInterceptor())
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_response_interceptor(ResponseDiagnosticsInterceptor())
lambda_handler = sb.lambda_handler()
