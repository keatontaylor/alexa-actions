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


class Operation(object):
    """
    An operation which adds, removes or replaces item(s) defined in a dynamicIndexList.


    :param object_type: Defines the operation type and dictates which properties must/can be included.
    :type object_type: (optional) str
    :param index: The position of the item in the dynamicIndexList to which the operation is to be applied. For inserts and deletes that operate on multiple items, this value represents the starting index, with onward inserts/deletes applying to consecutively increasing positions.
    :type index: (optional) int

    .. note::

        This is an abstract class. Use the following mapping, to figure out
        the model class to be instantiated, that sets ``type`` variable.

        | SetItem: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.set_item_operation.SetItemOperation`,
        |
        | InsertMultipleItems: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.insert_multiple_items_operation.InsertMultipleItemsOperation`,
        |
        | DeleteMultipleItems: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.delete_multiple_items_operation.DeleteMultipleItemsOperation`,
        |
        | InsertItem: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.insert_item_operation.InsertItemOperation`,
        |
        | DeleteItem: :py:class:`ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.delete_item_operation.DeleteItemOperation`

    """
    deserialized_types = {
        'object_type': 'str',
        'index': 'int'
    }  # type: Dict

    attribute_map = {
        'object_type': 'type',
        'index': 'index'
    }  # type: Dict
    supports_multiple_types = False

    discriminator_value_class_map = {
        'SetItem': 'ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.set_item_operation.SetItemOperation',
        'InsertMultipleItems': 'ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.insert_multiple_items_operation.InsertMultipleItemsOperation',
        'DeleteMultipleItems': 'ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.delete_multiple_items_operation.DeleteMultipleItemsOperation',
        'InsertItem': 'ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.insert_item_operation.InsertItemOperation',
        'DeleteItem': 'ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.delete_item_operation.DeleteItemOperation'
    }

    json_discriminator_key = "type"

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, object_type=None, index=None):
        # type: (Optional[str], Optional[int]) -> None
        """An operation which adds, removes or replaces item(s) defined in a dynamicIndexList.

        :param object_type: Defines the operation type and dictates which properties must/can be included.
        :type object_type: (optional) str
        :param index: The position of the item in the dynamicIndexList to which the operation is to be applied. For inserts and deletes that operate on multiple items, this value represents the starting index, with onward inserts/deletes applying to consecutively increasing positions.
        :type index: (optional) int
        """
        self.__discriminator_value = None  # type: str

        self.object_type = object_type
        self.index = index

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
        if not isinstance(other, Operation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
