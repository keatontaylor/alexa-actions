# coding: utf-8

#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#

import pprint
import re  # noqa: F401
import six
import typing
from enum import Enum
from abc import ABCMeta, abstractmethod


if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Union, Any
    from datetime import datetime


class Directive(object):
    """

    :param object_type: 
    :type object_type: (optional) str

    .. note::

        This is an abstract class. Use the following mapping, to figure out
        the model class to be instantiated, that sets ``type`` variable.

        | CustomInterfaceController.StopEventHandler: :py:class:`ask_sdk_model.interfaces.custom_interface_controller.stop_event_handler_directive.StopEventHandlerDirective`,
        |
        | Navigation.Assistance.AnnounceRoadRegulation: :py:class:`ask_sdk_model.interfaces.navigation.assistance.announce_road_regulation.AnnounceRoadRegulation`,
        |
        | Connections.SendRequest: :py:class:`ask_sdk_model.interfaces.connections.send_request_directive.SendRequestDirective`,
        |
        | Dialog.UpdateDynamicEntities: :py:class:`ask_sdk_model.dialog.dynamic_entities_directive.DynamicEntitiesDirective`,
        |
        | CustomInterfaceController.StartEventHandler: :py:class:`ask_sdk_model.interfaces.custom_interface_controller.start_event_handler_directive.StartEventHandlerDirective`,
        |
        | GadgetController.SetLight: :py:class:`ask_sdk_model.interfaces.gadget_controller.set_light_directive.SetLightDirective`,
        |
        | Alexa.Presentation.APL.SendIndexListData: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.send_index_list_data_directive.SendIndexListDataDirective`,
        |
        | Dialog.Delegate: :py:class:`ask_sdk_model.dialog.delegate_directive.DelegateDirective`,
        |
        | Dialog.ConfirmIntent: :py:class:`ask_sdk_model.dialog.confirm_intent_directive.ConfirmIntentDirective`,
        |
        | Alexa.Advertisement.InjectAds: :py:class:`ask_sdk_model.interfaces.alexa.advertisement.inject_ads.InjectAds`,
        |
        | CustomInterfaceController.SendDirective: :py:class:`ask_sdk_model.interfaces.custom_interface_controller.send_directive_directive.SendDirectiveDirective`,
        |
        | Alexa.Presentation.HTML.HandleMessage: :py:class:`ask_sdk_model.interfaces.alexa.presentation.html.handle_message_directive.HandleMessageDirective`,
        |
        | Alexa.Presentation.APLA.RenderDocument: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apla.render_document_directive.RenderDocumentDirective`,
        |
        | Dialog.ElicitSlot: :py:class:`ask_sdk_model.dialog.elicit_slot_directive.ElicitSlotDirective`,
        |
        | Alexa.Presentation.HTML.Start: :py:class:`ask_sdk_model.interfaces.alexa.presentation.html.start_directive.StartDirective`,
        |
        | Alexa.SmartVision.SnapshotProvider.GetSnapshotDirective: :py:class:`ask_sdk_model.interfaces.alexa.smartvision.snapshotprovider.get_snapshot_directive.GetSnapshotDirective`,
        |
        | AudioPlayer.Stop: :py:class:`ask_sdk_model.interfaces.audioplayer.stop_directive.StopDirective`,
        |
        | Dialog.ConfirmSlot: :py:class:`ask_sdk_model.dialog.confirm_slot_directive.ConfirmSlotDirective`,
        |
        | AudioPlayer.Play: :py:class:`ask_sdk_model.interfaces.audioplayer.play_directive.PlayDirective`,
        |
        | Alexa.Presentation.APL.ExecuteCommands: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.execute_commands_directive.ExecuteCommandsDirective`,
        |
        | Display.RenderTemplate: :py:class:`ask_sdk_model.interfaces.display.render_template_directive.RenderTemplateDirective`,
        |
        | Conversations.ResetContext: :py:class:`ask_sdk_model.interfaces.conversations.reset_context_directive.ResetContextDirective`,
        |
        | Dialog.DelegateRequest: :py:class:`ask_sdk_model.dialog.delegate_request_directive.DelegateRequestDirective`,
        |
        | Hint: :py:class:`ask_sdk_model.interfaces.display.hint_directive.HintDirective`,
        |
        | Connections.StartConnection: :py:class:`ask_sdk_model.interfaces.connections.v1.start_connection_directive.StartConnectionDirective`,
        |
        | Alexa.Presentation.APLT.RenderDocument: :py:class:`ask_sdk_model.interfaces.alexa.presentation.aplt.render_document_directive.RenderDocumentDirective`,
        |
        | GameEngine.StartInputHandler: :py:class:`ask_sdk_model.interfaces.game_engine.start_input_handler_directive.StartInputHandlerDirective`,
        |
        | VideoApp.Launch: :py:class:`ask_sdk_model.interfaces.videoapp.launch_directive.LaunchDirective`,
        |
        | Alexa.Presentation.APLT.ExecuteCommands: :py:class:`ask_sdk_model.interfaces.alexa.presentation.aplt.execute_commands_directive.ExecuteCommandsDirective`,
        |
        | GameEngine.StopInputHandler: :py:class:`ask_sdk_model.interfaces.game_engine.stop_input_handler_directive.StopInputHandlerDirective`,
        |
        | Tasks.CompleteTask: :py:class:`ask_sdk_model.interfaces.tasks.complete_task_directive.CompleteTaskDirective`,
        |
        | Alexa.Presentation.APL.RenderDocument: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.render_document_directive.RenderDocumentDirective`,
        |
        | Connections.SendResponse: :py:class:`ask_sdk_model.interfaces.connections.send_response_directive.SendResponseDirective`,
        |
        | Alexa.Presentation.APL.SendTokenListData: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.send_token_list_data_directive.SendTokenListDataDirective`,
        |
        | AudioPlayer.ClearQueue: :py:class:`ask_sdk_model.interfaces.audioplayer.clear_queue_directive.ClearQueueDirective`,
        |
        | Alexa.Presentation.APL.UpdateIndexListData: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.update_index_list_data_directive.UpdateIndexListDataDirective`

    """
    deserialized_types = {
        'object_type': 'str'
    }  # type: Dict

    attribute_map = {
        'object_type': 'type'
    }  # type: Dict
    supports_multiple_types = False

    discriminator_value_class_map = {
        'CustomInterfaceController.StopEventHandler': 'ask_sdk_model.interfaces.custom_interface_controller.stop_event_handler_directive.StopEventHandlerDirective',
        'Navigation.Assistance.AnnounceRoadRegulation': 'ask_sdk_model.interfaces.navigation.assistance.announce_road_regulation.AnnounceRoadRegulation',
        'Connections.SendRequest': 'ask_sdk_model.interfaces.connections.send_request_directive.SendRequestDirective',
        'Dialog.UpdateDynamicEntities': 'ask_sdk_model.dialog.dynamic_entities_directive.DynamicEntitiesDirective',
        'CustomInterfaceController.StartEventHandler': 'ask_sdk_model.interfaces.custom_interface_controller.start_event_handler_directive.StartEventHandlerDirective',
        'GadgetController.SetLight': 'ask_sdk_model.interfaces.gadget_controller.set_light_directive.SetLightDirective',
        'Alexa.Presentation.APL.SendIndexListData': 'ask_sdk_model.interfaces.alexa.presentation.apl.send_index_list_data_directive.SendIndexListDataDirective',
        'Dialog.Delegate': 'ask_sdk_model.dialog.delegate_directive.DelegateDirective',
        'Dialog.ConfirmIntent': 'ask_sdk_model.dialog.confirm_intent_directive.ConfirmIntentDirective',
        'Alexa.Advertisement.InjectAds': 'ask_sdk_model.interfaces.alexa.advertisement.inject_ads.InjectAds',
        'CustomInterfaceController.SendDirective': 'ask_sdk_model.interfaces.custom_interface_controller.send_directive_directive.SendDirectiveDirective',
        'Alexa.Presentation.HTML.HandleMessage': 'ask_sdk_model.interfaces.alexa.presentation.html.handle_message_directive.HandleMessageDirective',
        'Alexa.Presentation.APLA.RenderDocument': 'ask_sdk_model.interfaces.alexa.presentation.apla.render_document_directive.RenderDocumentDirective',
        'Dialog.ElicitSlot': 'ask_sdk_model.dialog.elicit_slot_directive.ElicitSlotDirective',
        'Alexa.Presentation.HTML.Start': 'ask_sdk_model.interfaces.alexa.presentation.html.start_directive.StartDirective',
        'Alexa.SmartVision.SnapshotProvider.GetSnapshotDirective': 'ask_sdk_model.interfaces.alexa.smartvision.snapshotprovider.get_snapshot_directive.GetSnapshotDirective',
        'AudioPlayer.Stop': 'ask_sdk_model.interfaces.audioplayer.stop_directive.StopDirective',
        'Dialog.ConfirmSlot': 'ask_sdk_model.dialog.confirm_slot_directive.ConfirmSlotDirective',
        'AudioPlayer.Play': 'ask_sdk_model.interfaces.audioplayer.play_directive.PlayDirective',
        'Alexa.Presentation.APL.ExecuteCommands': 'ask_sdk_model.interfaces.alexa.presentation.apl.execute_commands_directive.ExecuteCommandsDirective',
        'Display.RenderTemplate': 'ask_sdk_model.interfaces.display.render_template_directive.RenderTemplateDirective',
        'Conversations.ResetContext': 'ask_sdk_model.interfaces.conversations.reset_context_directive.ResetContextDirective',
        'Dialog.DelegateRequest': 'ask_sdk_model.dialog.delegate_request_directive.DelegateRequestDirective',
        'Hint': 'ask_sdk_model.interfaces.display.hint_directive.HintDirective',
        'Connections.StartConnection': 'ask_sdk_model.interfaces.connections.v1.start_connection_directive.StartConnectionDirective',
        'Alexa.Presentation.APLT.RenderDocument': 'ask_sdk_model.interfaces.alexa.presentation.aplt.render_document_directive.RenderDocumentDirective',
        'GameEngine.StartInputHandler': 'ask_sdk_model.interfaces.game_engine.start_input_handler_directive.StartInputHandlerDirective',
        'VideoApp.Launch': 'ask_sdk_model.interfaces.videoapp.launch_directive.LaunchDirective',
        'Alexa.Presentation.APLT.ExecuteCommands': 'ask_sdk_model.interfaces.alexa.presentation.aplt.execute_commands_directive.ExecuteCommandsDirective',
        'GameEngine.StopInputHandler': 'ask_sdk_model.interfaces.game_engine.stop_input_handler_directive.StopInputHandlerDirective',
        'Tasks.CompleteTask': 'ask_sdk_model.interfaces.tasks.complete_task_directive.CompleteTaskDirective',
        'Alexa.Presentation.APL.RenderDocument': 'ask_sdk_model.interfaces.alexa.presentation.apl.render_document_directive.RenderDocumentDirective',
        'Connections.SendResponse': 'ask_sdk_model.interfaces.connections.send_response_directive.SendResponseDirective',
        'Alexa.Presentation.APL.SendTokenListData': 'ask_sdk_model.interfaces.alexa.presentation.apl.send_token_list_data_directive.SendTokenListDataDirective',
        'AudioPlayer.ClearQueue': 'ask_sdk_model.interfaces.audioplayer.clear_queue_directive.ClearQueueDirective',
        'Alexa.Presentation.APL.UpdateIndexListData': 'ask_sdk_model.interfaces.alexa.presentation.apl.update_index_list_data_directive.UpdateIndexListDataDirective'
    }

    json_discriminator_key = "type"

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, object_type=None):
        # type: (Optional[str]) -> None
        """

        :param object_type: 
        :type object_type: (optional) str
        """
        self.__discriminator_value = None  # type: str

        self.object_type = object_type

    @classmethod
    def get_real_child_model(cls, data):
        # type: (Dict[str, str]) -> Optional[str]
        """Returns the real base class specified by the discriminator"""
        discriminator_value = data[cls.json_discriminator_key]
        return cls.discriminator_value_class_map.get(discriminator_value)

    def to_dict(self):
        # type: () -> Dict[str, object]
        """Returns the model properties as a dict"""
        result = {}  # type: Dict

        for attr, _ in six.iteritems(self.deserialized_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else
                    x.value if isinstance(x, Enum) else x,
                    value
                ))
            elif isinstance(value, Enum):
                result[attr] = value.value
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else
                    (item[0], item[1].value)
                    if isinstance(item[1], Enum) else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        # type: () -> str
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        # type: () -> str
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are equal"""
        if not isinstance(other, Directive):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
