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


class Command(object):
    """
    DataStore command which will run in DataStore.


    :param object_type: The type of the component. Allowed values are * &#x60;PUT_OBJECT&#x60; - Creates or updates an object. * &#x60;PUT_NAMESPACE&#x60; - Creates a new namespace. If the namespace already exists, the command succeeds without any change. * &#x60;REMOVE_OBJECT&#x60; - Deletes an existing object. If the object doesn&#39;t exist, this command succeeds without any change. * &#x60;REMOVE_NAMESPACE&#x60; - Deletes an existing namespace. If the namespace doesn&#39;t exist, this command succeeds without any change. * &#x60;CLEAR&#x60; - Remove all existing data in skill&#39;s DataStore. 
    :type object_type: (optional) str

    .. note::

        This is an abstract class. Use the following mapping, to figure out
        the model class to be instantiated, that sets ``type`` variable.

        | REMOVE_NAMESPACE: :py:class:`ask_sdk_model.services.datastore.v1.remove_namespace_command.RemoveNamespaceCommand`,
        |
        | REMOVE_OBJECT: :py:class:`ask_sdk_model.services.datastore.v1.remove_object_command.RemoveObjectCommand`,
        |
        | PUT_OBJECT: :py:class:`ask_sdk_model.services.datastore.v1.put_object_command.PutObjectCommand`,
        |
        | CLEAR: :py:class:`ask_sdk_model.services.datastore.v1.clear_command.ClearCommand`,
        |
        | PUT_NAMESPACE: :py:class:`ask_sdk_model.services.datastore.v1.put_namespace_command.PutNamespaceCommand`

    """
    deserialized_types = {
        'object_type': 'str'
    }  # type: Dict

    attribute_map = {
        'object_type': 'type'
    }  # type: Dict
    supports_multiple_types = False

    discriminator_value_class_map = {
        'REMOVE_NAMESPACE': 'ask_sdk_model.services.datastore.v1.remove_namespace_command.RemoveNamespaceCommand',
        'REMOVE_OBJECT': 'ask_sdk_model.services.datastore.v1.remove_object_command.RemoveObjectCommand',
        'PUT_OBJECT': 'ask_sdk_model.services.datastore.v1.put_object_command.PutObjectCommand',
        'CLEAR': 'ask_sdk_model.services.datastore.v1.clear_command.ClearCommand',
        'PUT_NAMESPACE': 'ask_sdk_model.services.datastore.v1.put_namespace_command.PutNamespaceCommand'
    }

    json_discriminator_key = "type"

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, object_type=None):
        # type: (Optional[str]) -> None
        """DataStore command which will run in DataStore.

        :param object_type: The type of the component. Allowed values are * &#x60;PUT_OBJECT&#x60; - Creates or updates an object. * &#x60;PUT_NAMESPACE&#x60; - Creates a new namespace. If the namespace already exists, the command succeeds without any change. * &#x60;REMOVE_OBJECT&#x60; - Deletes an existing object. If the object doesn&#39;t exist, this command succeeds without any change. * &#x60;REMOVE_NAMESPACE&#x60; - Deletes an existing namespace. If the namespace doesn&#39;t exist, this command succeeds without any change. * &#x60;CLEAR&#x60; - Remove all existing data in skill&#39;s DataStore. 
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
        if not isinstance(other, Command):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
