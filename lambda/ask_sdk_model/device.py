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


if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Union, Any
    from datetime import datetime
    from ask_sdk_model.supported_interfaces import SupportedInterfaces as SupportedInterfaces_8ec830f5


class Device(object):
    """
    An object providing information about the device used to send the request. The device object contains both deviceId and supportedInterfaces properties. The deviceId property uniquely identifies the device. The supportedInterfaces property lists each interface that the device supports. For example, if supportedInterfaces includes AudioPlayer {}, then you know that the device supports streaming audio using the AudioPlayer interface.


    :param device_id: The deviceId property uniquely identifies the device. This identifier is scoped to a skill. Normally, disabling and re-enabling a skill generates a new identifier.
    :type device_id: (optional) str
    :param persistent_endpoint_id: A persistent identifier for the Endpoint ID where the skill request is issued from. An endpoint represents an Alexa-connected Endpoint (like an Echo device, or an application) with which an Alexa customer can interact rather than a physical device,  so it could represent applications on your fire TV or your Alexa phone app.  The persistentEndpointId is a string that represents a unique identifier for the endpoint in the context of a request.  It is in the Amazon Common Identifier format \&quot;amzn1.alexa.endpoint.did.{id}\&quot;. This identifier space is scoped to a vendor, therefore it will stay the same regardless of skill enablement.
    :type persistent_endpoint_id: (optional) str
    :param supported_interfaces: Lists each interface that the device supports. For example, if supportedInterfaces includes AudioPlayer {}, then you know that the device supports streaming audio using the AudioPlayer interface
    :type supported_interfaces: (optional) ask_sdk_model.supported_interfaces.SupportedInterfaces

    """
    deserialized_types = {
        'device_id': 'str',
        'persistent_endpoint_id': 'str',
        'supported_interfaces': 'ask_sdk_model.supported_interfaces.SupportedInterfaces'
    }  # type: Dict

    attribute_map = {
        'device_id': 'deviceId',
        'persistent_endpoint_id': 'persistentEndpointId',
        'supported_interfaces': 'supportedInterfaces'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, device_id=None, persistent_endpoint_id=None, supported_interfaces=None):
        # type: (Optional[str], Optional[str], Optional[SupportedInterfaces_8ec830f5]) -> None
        """An object providing information about the device used to send the request. The device object contains both deviceId and supportedInterfaces properties. The deviceId property uniquely identifies the device. The supportedInterfaces property lists each interface that the device supports. For example, if supportedInterfaces includes AudioPlayer {}, then you know that the device supports streaming audio using the AudioPlayer interface.

        :param device_id: The deviceId property uniquely identifies the device. This identifier is scoped to a skill. Normally, disabling and re-enabling a skill generates a new identifier.
        :type device_id: (optional) str
        :param persistent_endpoint_id: A persistent identifier for the Endpoint ID where the skill request is issued from. An endpoint represents an Alexa-connected Endpoint (like an Echo device, or an application) with which an Alexa customer can interact rather than a physical device,  so it could represent applications on your fire TV or your Alexa phone app.  The persistentEndpointId is a string that represents a unique identifier for the endpoint in the context of a request.  It is in the Amazon Common Identifier format \&quot;amzn1.alexa.endpoint.did.{id}\&quot;. This identifier space is scoped to a vendor, therefore it will stay the same regardless of skill enablement.
        :type persistent_endpoint_id: (optional) str
        :param supported_interfaces: Lists each interface that the device supports. For example, if supportedInterfaces includes AudioPlayer {}, then you know that the device supports streaming audio using the AudioPlayer interface
        :type supported_interfaces: (optional) ask_sdk_model.supported_interfaces.SupportedInterfaces
        """
        self.__discriminator_value = None  # type: str

        self.device_id = device_id
        self.persistent_endpoint_id = persistent_endpoint_id
        self.supported_interfaces = supported_interfaces

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
        if not isinstance(other, Device):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
