"""HA transport, notification snapshots and response delivery."""

import json
import hashlib
from typing import Optional

import urllib3
from ask_sdk_core.utils import get_account_linking_access_token, is_request_type, get_slot
from ask_sdk_model.slu.entityresolution import StatusCode
from pydantic import ValidationError

import prompts
from const import INPUT_TEXT_ENTITY, RESPONSE_YES, RESPONSE_NO
from schemas import HaState, HaStateError
from utils import get_logger

SESSION_KEY = "alexa_actionable_notification"
COMPLETED_KEY = "alexa_actionable_notification_completed"
logger = get_logger(False)


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


class HomeAssistantClient:
    """One request's HA client, with notification context carried by Alexa's session."""

    def __init__(self, handler_input, settings, http):
        self.handler_input = handler_input
        self.ha_state = None
        self.http = http
        self.settings = settings
        attributes = handler_input.attributes_manager
        attributes.request_attributes["ha"] = self
        self.language_strings = attributes.request_attributes["_"]
        self.session = attributes.session_attributes
        self.token = settings.TOKEN or get_account_linking_access_token(handler_input)
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

    def _build_url(self, *path):
        return f"{self.settings.HOME_ASSISTANT_URL.rstrip('/')}/" + "/".join(path)

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
                confirmation_yes=state.get("confirmation_yes"),
                confirmation_no=state.get("confirmation_no"),
                group=_string_to_bool(state.get("group")),
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
        if self.settings.INCLUDE_DEVICE_ID and system.device and system.device.device_id:
            body["event_device_id"] = system.device.device_id
        if state.group and system.device and system.device.device_id:
            # Compact, stable identity for counting distinct silent group members.
            body["event_device_key"] = hashlib.sha256(system.device.device_id.encode()).hexdigest()[:16]
        if self._post("api", "events", "alexa_actionable_notification", body=body) is None:
            return self.ha_state.text
        self.completed = True
        self.session[COMPLETED_KEY] = True
        if state.suppress_confirmation:
            return ""
        custom = {RESPONSE_YES: state.confirmation_yes, RESPONSE_NO: state.confirmation_no}.get(response_type)
        return custom if custom is not None else self.language_strings[prompts.OKAY]

    def post_command(self, text, intent):
        """Standalone commands never read the notification helper or reuse its event ID."""
        if not self.settings.ENABLE_COMMANDS:
            return "Standalone commands are disabled in this skill."
        if self.ha_state is not None:
            return "Please answer or stop the current question before giving a command."
        body = {"command": text, "intent": intent, "request_id": self.handler_input.request_envelope.request.request_id}
        system = self.handler_input.request_envelope.context.system
        if system.person and system.person.person_id:
            body["event_person_id"] = system.person.person_id
        if self.settings.INCLUDE_DEVICE_ID and system.device and system.device.device_id:
            body["event_device_id"] = system.device.device_id
        if self.session.get("alexa_actionable_command_completed") == body["request_id"]:
            return ""
        if self._post("api", "events", "alexa_actionable_command", body=body) is None:
            return self.ha_state.text
        self.session["alexa_actionable_command_completed"] = body["request_id"]
        return self.language_strings[prompts.OKAY]

    def get_value_for_slot(self, slot_name):
        slot = get_slot(self.handler_input, slot_name=slot_name)
        if slot and slot.resolutions and slot.resolutions.resolutions_per_authority:
            for resolution in slot.resolutions.resolutions_per_authority:
                if resolution.status.code == StatusCode.ER_SUCCESS_MATCH:
                    for value in resolution.values or []:
                        if value.value and value.value.name:
                            return value.value.name
        return None
