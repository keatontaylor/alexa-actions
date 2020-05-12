## VERSION 0.4

import logging
import urllib3
import json

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# UPDATE THESE VARIABLES WITH YOUR CONFIG
HOME_ASSISTANT_URL                = "https://waesqq0rw2rzmaummr8xbc39jmavoce4.ui.nabu.casa"       # REPLACE WITH THE URL FOR YOUR HA FRONTEND
VERIFY_SSL                        = False                              # SET TO FALSE IF YOU DO NOT HAVE VALID CERTS
TOKEN                             = ""                                # ADD YOUR LONG LIVED TOKEN IF NEEDED OTHERWISE LEAVE BLANK

home_assistant_object = None
class HomeAssistant():
    """Class to abstract access to HA."""
    def __init__(self, handler_input):
        self.event_id = ""
        self.text = ""
        self.handler_input = handler_input
        
        self.token = self._fetch_token(handler_input) if TOKEN == "" else TOKEN
        
        # added for variable responses from Alexa
        self.response_text_yes = ""
        self.response_text_no = ""
        self.response_text = ""

    def _fetch_token(self, handler_input):
        return ask_utils.get_account_linking_access_token(handler_input)
        
    def get_health_check(self):
        """Check connection to HA."""
        
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=2.0, read=10.0)
        )
        
        response = http.request(
            'GET', 
            '{}/api/config'.format(HOME_ASSISTANT_URL),
            headers={
                'Authorization': 'Bearer {}'.format(self.token),
                'Content-Type': 'application/json',
            },
        )
        
        if response.status >= 400:
            print(response.data)
            return "Could not communicate with home assistant"
        
        return "Communication with home assistant successful"
        
    def get_ha_state(self):
        """Get State from HA."""
        
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=2.0, read=10.0)
        )
        
        response = http.request(
            'GET', 
            '{}/api/states/{}'.format(HOME_ASSISTANT_URL, "input_text.alexa_actionable_notification"),
            headers={
                'Authorization': 'Bearer {}'.format(self.token),
                'Content-Type': 'application/json',
            },
        )
        
        if response.status >= 400:
            print(response.data)
            return "Could not communicate with home assistant"
            
        decoded_response = json.loads(response.data.decode('utf-8'))['state']
        
        self.event_id =  json.loads(decoded_response)['event']
        self.text = json.loads(decoded_response)['text']
        # added for variable responses from Alexa
        self.response_text_yes = json.loads(decoded_response)['response_yes']
        self.response_text_no = json.loads(decoded_response)['response_no']
        
        return self.text
        
    def post_ha_event(self, response: str):
        """Send event to HA."""
        
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=2.0, read=10.0)
        )
        # added for variable responses from Alexa
        if response == 'ResponseYes':
            self.response_text = self.response_text_yes
        elif response == 'ResponseNo':
            self.response_text = self.response_text_no
            
        response = http.request(
            'POST', 
            '{}/api/events/alexa_actionable_notification'.format(HOME_ASSISTANT_URL),
            headers={
                'Authorization': 'Bearer {}'.format(self.token),
                'Content-Type': 'application/json',
            },
            body=json.dumps({"event_id": self.event_id, "event_response": response, "text": self.text}).encode('utf-8')
        )
        

        if response.status >= 400:
            return "Could not communicate with home assistant"
        # changed  for variable responses from Alexa
        return self.response_text


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global home_assistant_object
        home_assistant_object = HomeAssistant(handler_input)
        speak_output = home_assistant_object.get_ha_state()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask('')
                .response
        )


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global home_assistant_object
        if home_assistant_object == None:
            home_assistant_object = HomeAssistant(handler_input)
            home_assistant_object.get_ha_state()
        
        speak_output = home_assistant_object.post_ha_event("ResponseYes")
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class NoIntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global home_assistant_object
        if home_assistant_object == None:
            home_assistant_object = HomeAssistant(handler_input)
            home_assistant_object.get_ha_state()
        
        speak_output = home_assistant_object.post_ha_event("ResponseNo")
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class SelectIntentHandler(AbstractRequestHandler):
    """Handler for Select Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Select")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        selection  = ask_utils.get_slot_value(
            handler_input=handler_input, slot_name="Selections")

        global home_assistant_object
        if home_assistant_object == None:
            home_assistant_object = HomeAssistant(handler_input)
            home_assistant_object.get_ha_state()
            

        home_assistant_object.post_ha_event(selection)
        speak_output = "You selected " + selection
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        global home_assistant_object
        home_assistant_object = HomeAssistant(handler_input)
        speak_output = home_assistant_object.get_health_check()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        print("CancelOrStopIntentHandler")
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        global home_assistant_object
        if home_assistant_object == None:
            home_assistant_object = HomeAssistant(handler_input)
            home_assistant_object.get_ha_state()

        speak_output = home_assistant_object.post_ha_event("ResponseNone")

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        print("IntentReflectorHandler")
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        print("CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(SelectIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
