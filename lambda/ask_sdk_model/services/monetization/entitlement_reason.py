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


class EntitlementReason(Enum):
    """
    Reason for the entitlement status. * &#39;PURCHASED&#39; - The user is entitled to the product because they purchased it directly. * &#39;NOT_PURCHASED&#39; - The user is not entitled to the product because they have not purchased it. * &#39;AUTO_ENTITLED&#39; - The user is auto entitled to the product because they have subscribed to a broader service. * &#39;BUNDLE_ENTITLED&#39; - The user is entitled to the product because they purchased it indirectly as part of a bundle. If the user is entitled via both PURCHASED and BUNDLE_ENTITLED, then BUNDLE_ENTITLED takes priority.



    Allowed enum values: [PURCHASED, NOT_PURCHASED, AUTO_ENTITLED, BUNDLE_ENTITLED]
    """
    PURCHASED = "PURCHASED"
    NOT_PURCHASED = "NOT_PURCHASED"
    AUTO_ENTITLED = "AUTO_ENTITLED"
    BUNDLE_ENTITLED = "BUNDLE_ENTITLED"

    def to_dict(self):
        # type: () -> Dict[str, Any]
        """Returns the model properties as a dict"""
        result = {self.name: self.value}
        return result

    def to_str(self):
        # type: () -> str
        """Returns the string representation of the model"""
        return pprint.pformat(self.value)

    def __repr__(self):
        # type: () -> str
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        # type: (Any) -> bool
        """Returns true if both objects are equal"""
        if not isinstance(other, EntitlementReason):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (Any) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
