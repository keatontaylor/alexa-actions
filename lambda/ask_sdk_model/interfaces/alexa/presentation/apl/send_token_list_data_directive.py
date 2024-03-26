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


class SendTokenListDataDirective(Directive):
    """
    Returned in response to a LoadTokenListData event, containing the requested items and metadata for further interaction.


    :param correlation_token: The correlation token supplied in the LoadTokenListData event. This parameter is mandatory if the skill is responding to a LoadTokenListData request, the skill response will be rejected if the expected correlationToken is not specified.
    :type correlation_token: (optional) str
    :param list_id: The identifier of the list whose items are contained in this response.
    :type list_id: (optional) str
    :param page_token: Opaque token for the array of items which are contained in this response. Ignored by the system if correlationToken is specified, but considered less cognitive overhead to have the developer always include &amp; assists platform debugging.
    :type page_token: (optional) str
    :param next_page_token: Opaque token to retrieve the next page of list items data. Absence of this property indicates that the last item in the list has been reached in the scroll direction.
    :type next_page_token: (optional) str
    :param items: Array of objects to be added to the device cache.
    :type items: (optional) list[object]

    """
    deserialized_types = {
        'object_type': 'str',
        'correlation_token': 'str',
        'list_id': 'str',
        'page_token': 'str',
        'next_page_token': 'str',
        'items': 'list[object]'
    }  # type: Dict

    attribute_map = {
        'object_type': 'type',
        'correlation_token': 'correlationToken',
        'list_id': 'listId',
        'page_token': 'pageToken',
        'next_page_token': 'nextPageToken',
        'items': 'items'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, correlation_token=None, list_id=None, page_token=None, next_page_token=None, items=None):
        # type: (Optional[str], Optional[str], Optional[str], Optional[str], Optional[List[object]]) -> None
        """Returned in response to a LoadTokenListData event, containing the requested items and metadata for further interaction.

        :param correlation_token: The correlation token supplied in the LoadTokenListData event. This parameter is mandatory if the skill is responding to a LoadTokenListData request, the skill response will be rejected if the expected correlationToken is not specified.
        :type correlation_token: (optional) str
        :param list_id: The identifier of the list whose items are contained in this response.
        :type list_id: (optional) str
        :param page_token: Opaque token for the array of items which are contained in this response. Ignored by the system if correlationToken is specified, but considered less cognitive overhead to have the developer always include &amp; assists platform debugging.
        :type page_token: (optional) str
        :param next_page_token: Opaque token to retrieve the next page of list items data. Absence of this property indicates that the last item in the list has been reached in the scroll direction.
        :type next_page_token: (optional) str
        :param items: Array of objects to be added to the device cache.
        :type items: (optional) list[object]
        """
        self.__discriminator_value = "Alexa.Presentation.APL.SendTokenListData"  # type: str

        self.object_type = self.__discriminator_value
        super(SendTokenListDataDirective, self).__init__(object_type=self.__discriminator_value)
        self.correlation_token = correlation_token
        self.list_id = list_id
        self.page_token = page_token
        self.next_page_token = next_page_token
        self.items = items

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
        if not isinstance(other, SendTokenListDataDirective):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
