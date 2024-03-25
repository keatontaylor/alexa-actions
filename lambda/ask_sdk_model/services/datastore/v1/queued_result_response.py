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
    from ask_sdk_model.services.datastore.v1.response_pagination_context import ResponsePaginationContext as ResponsePaginationContext_2e377452
    from ask_sdk_model.services.datastore.v1.commands_dispatch_result import CommandsDispatchResult as CommandsDispatchResult_a4ae4026


class QueuedResultResponse(object):
    """
    Response for queued deliveries query.


    :param items: The array only contains results which have not been a SUCCESS delivery. An empty response means that all targeted devices has been received the commands payload. 
    :type items: (optional) list[ask_sdk_model.services.datastore.v1.commands_dispatch_result.CommandsDispatchResult]
    :param pagination_context: 
    :type pagination_context: (optional) ask_sdk_model.services.datastore.v1.response_pagination_context.ResponsePaginationContext

    """
    deserialized_types = {
        'items': 'list[ask_sdk_model.services.datastore.v1.commands_dispatch_result.CommandsDispatchResult]',
        'pagination_context': 'ask_sdk_model.services.datastore.v1.response_pagination_context.ResponsePaginationContext'
    }  # type: Dict

    attribute_map = {
        'items': 'items',
        'pagination_context': 'paginationContext'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, items=None, pagination_context=None):
        # type: (Optional[List[CommandsDispatchResult_a4ae4026]], Optional[ResponsePaginationContext_2e377452]) -> None
        """Response for queued deliveries query.

        :param items: The array only contains results which have not been a SUCCESS delivery. An empty response means that all targeted devices has been received the commands payload. 
        :type items: (optional) list[ask_sdk_model.services.datastore.v1.commands_dispatch_result.CommandsDispatchResult]
        :param pagination_context: 
        :type pagination_context: (optional) ask_sdk_model.services.datastore.v1.response_pagination_context.ResponsePaginationContext
        """
        self.__discriminator_value = None  # type: str

        self.items = items
        self.pagination_context = pagination_context

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
        if not isinstance(other, QueuedResultResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
