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


class SendIndexListDataDirective(Directive):
    """
    Returned in response to a LoadIndexListData event, containing the requested items and metadata for further interaction.


    :param correlation_token: The correlation token supplied in the LoadTokenListData event. This parameter is mandatory if the skill is responding to a LoadIndexListData request, the skill response will be rejected if the expected correlationToken is not specified.
    :type correlation_token: (optional) str
    :param list_id: The identifier of the list whose items are contained in this response.
    :type list_id: (optional) str
    :param list_version: The new version of the list after loading the items supplied in this directive. List versions increase sequentially, implicitly starting at 0 for the definition specified in the presentation&#39;s RenderDocument directive.
    :type list_version: (optional) int
    :param start_index: Index of the first element in the items array. 
    :type start_index: (optional) int
    :param minimum_inclusive_index: The index of the 1st item in the skill-managed array. When populated, this value replaces any value that was specified in a previous interaction. Continued absence of this property indicates that the minimum index is not yet known and further backwards scrolling is possible. If this is equal to the index of the 1st item returned then no further backwards scrolling is possible.
    :type minimum_inclusive_index: (optional) int
    :param maximum_exclusive_index: The last valid index of the skill-managed array plus one, i.e. exclusive value. When populated, this value replaces any value that was specified in a previous interaction. Continued absence of this property indicates that the maximum index is not yet known and further forwards scrolling is possible. If this is one more than the index of the last item returned then no further forwards scrolling is possible.
    :type maximum_exclusive_index: (optional) int
    :param items: Array of objects to be added to the device cache.
    :type items: (optional) list[object]

    """
    deserialized_types = {
        'object_type': 'str',
        'correlation_token': 'str',
        'list_id': 'str',
        'list_version': 'int',
        'start_index': 'int',
        'minimum_inclusive_index': 'int',
        'maximum_exclusive_index': 'int',
        'items': 'list[object]'
    }  # type: Dict

    attribute_map = {
        'object_type': 'type',
        'correlation_token': 'correlationToken',
        'list_id': 'listId',
        'list_version': 'listVersion',
        'start_index': 'startIndex',
        'minimum_inclusive_index': 'minimumInclusiveIndex',
        'maximum_exclusive_index': 'maximumExclusiveIndex',
        'items': 'items'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, correlation_token=None, list_id=None, list_version=None, start_index=None, minimum_inclusive_index=None, maximum_exclusive_index=None, items=None):
        # type: (Optional[str], Optional[str], Optional[int], Optional[int], Optional[int], Optional[int], Optional[List[object]]) -> None
        """Returned in response to a LoadIndexListData event, containing the requested items and metadata for further interaction.

        :param correlation_token: The correlation token supplied in the LoadTokenListData event. This parameter is mandatory if the skill is responding to a LoadIndexListData request, the skill response will be rejected if the expected correlationToken is not specified.
        :type correlation_token: (optional) str
        :param list_id: The identifier of the list whose items are contained in this response.
        :type list_id: (optional) str
        :param list_version: The new version of the list after loading the items supplied in this directive. List versions increase sequentially, implicitly starting at 0 for the definition specified in the presentation&#39;s RenderDocument directive.
        :type list_version: (optional) int
        :param start_index: Index of the first element in the items array. 
        :type start_index: (optional) int
        :param minimum_inclusive_index: The index of the 1st item in the skill-managed array. When populated, this value replaces any value that was specified in a previous interaction. Continued absence of this property indicates that the minimum index is not yet known and further backwards scrolling is possible. If this is equal to the index of the 1st item returned then no further backwards scrolling is possible.
        :type minimum_inclusive_index: (optional) int
        :param maximum_exclusive_index: The last valid index of the skill-managed array plus one, i.e. exclusive value. When populated, this value replaces any value that was specified in a previous interaction. Continued absence of this property indicates that the maximum index is not yet known and further forwards scrolling is possible. If this is one more than the index of the last item returned then no further forwards scrolling is possible.
        :type maximum_exclusive_index: (optional) int
        :param items: Array of objects to be added to the device cache.
        :type items: (optional) list[object]
        """
        self.__discriminator_value = "Alexa.Presentation.APL.SendIndexListData"  # type: str

        self.object_type = self.__discriminator_value
        super(SendIndexListDataDirective, self).__init__(object_type=self.__discriminator_value)
        self.correlation_token = correlation_token
        self.list_id = list_id
        self.list_version = list_version
        self.start_index = start_index
        self.minimum_inclusive_index = minimum_inclusive_index
        self.maximum_exclusive_index = maximum_exclusive_index
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
        if not isinstance(other, SendIndexListDataDirective):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
