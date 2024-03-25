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


class QueuedResultRequestErrorType(Enum):
    """
    Error code of the response. * &#x60;NOT_FOUND&#x60; - queuedResultId is not found for the skill. * &#x60;INVALID_REQUEST&#x60; - One or more request parameters are invalid, see message for more details. * &#x60;INVALID_ACCESS_TOKEN&#x60; - Access token is expire or invalid. * &#x60;DATASTORE_SUPPORT_REQUIRED&#x60; - Client has not opted into DataStore interface in skill manifest. * &#x60;TOO_MANY_REQUESTS&#x60; - The request has been throttled because client has exceed maximum allowed request rate. * &#x60;DATASTORE_UNAVAILABLE&#x60; - Internal service error.



    Allowed enum values: [NOT_FOUND, INVALID_REQUEST, INVALID_ACCESS_TOKEN, DATASTORE_SUPPORT_REQUIRED, TOO_MANY_REQUESTS, DATASTORE_UNAVAILABLE]
    """
    NOT_FOUND = "NOT_FOUND"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_ACCESS_TOKEN = "INVALID_ACCESS_TOKEN"
    DATASTORE_SUPPORT_REQUIRED = "DATASTORE_SUPPORT_REQUIRED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    DATASTORE_UNAVAILABLE = "DATASTORE_UNAVAILABLE"

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
        if not isinstance(other, QueuedResultRequestErrorType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (Any) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
