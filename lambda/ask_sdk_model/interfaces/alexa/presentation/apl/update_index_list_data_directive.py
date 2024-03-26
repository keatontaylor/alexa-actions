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
from ask_sdk_model.directive import Directive


if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Union, Any
    from datetime import datetime
    from ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.operation import Operation as Operation_37040fb2


class UpdateIndexListDataDirective(Directive):
    """
    Updates the content of an dynamicIndexList datasource which has been previously communicated to an Alexa device.


    :param token: The unique identifier for the presentation containing the dynamicIndexList.
    :type token: (optional) str
    :param list_id: The identifier of the dynamicIndexList to update.
    :type list_id: (optional) str
    :param list_version: The new version of the list after applying the updates specified in this directive. List versions increase sequentially, implicitly starting at 0 for the definition specified in the presentation&#39;s RenderDocument directive.
    :type list_version: (optional) int
    :param operations: An array of changes which are to be applied to the items in the dynamicIndexList.
    :type operations: (optional) list[ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.operation.Operation]

    """
    deserialized_types = {
        'object_type': 'str',
        'token': 'str',
        'list_id': 'str',
        'list_version': 'int',
        'operations': 'list[ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.operation.Operation]'
    }  # type: Dict

    attribute_map = {
        'object_type': 'type',
        'token': 'token',
        'list_id': 'listId',
        'list_version': 'listVersion',
        'operations': 'operations'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, token=None, list_id=None, list_version=None, operations=None):
        # type: (Optional[str], Optional[str], Optional[int], Optional[List[Operation_37040fb2]]) -> None
        """Updates the content of an dynamicIndexList datasource which has been previously communicated to an Alexa device.

        :param token: The unique identifier for the presentation containing the dynamicIndexList.
        :type token: (optional) str
        :param list_id: The identifier of the dynamicIndexList to update.
        :type list_id: (optional) str
        :param list_version: The new version of the list after applying the updates specified in this directive. List versions increase sequentially, implicitly starting at 0 for the definition specified in the presentation&#39;s RenderDocument directive.
        :type list_version: (optional) int
        :param operations: An array of changes which are to be applied to the items in the dynamicIndexList.
        :type operations: (optional) list[ask_sdk_model.interfaces.alexa.presentation.apl.listoperations.operation.Operation]
        """
        self.__discriminator_value = "Alexa.Presentation.APL.UpdateIndexListData"  # type: str

        self.object_type = self.__discriminator_value
        super(UpdateIndexListDataDirective, self).__init__(object_type=self.__discriminator_value)
        self.token = token
        self.list_id = list_id
        self.list_version = list_version
        self.operations = operations

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
        if not isinstance(other, UpdateIndexListDataDirective):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
