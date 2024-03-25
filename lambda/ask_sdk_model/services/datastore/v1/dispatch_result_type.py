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


class DispatchResultType(Enum):
    """
    Defines success or a type of error from dispatch. * &#x60;SUCCESS&#x60; - device has received the payload. * &#x60;INVALID_DEVICE&#x60; - device is not capable of processing the payload. * &#x60;DEVICE_UNAVAILABLE&#x60; - dispatch failed because device is offline. * &#x60;DEVICE_PERMANENTLY_UNAVAILABLE&#x60; - target no longer available to receive data. This is reported for a failed delivery attempt related to an unregistered device. * &#x60;CONCURRENCY_ERROR&#x60; - there are concurrent attempts to update to the same device. * &#x60;INTERNAL_ERROR&#x60;- dispatch failed because of unknown error - see message. * &#x60;PENDING_REQUEST_COUNT_EXCEEDS_LIMIT&#x60; - the count of pending requests exceeds the limit. 



    Allowed enum values: [SUCCESS, INVALID_DEVICE, DEVICE_UNAVAILABLE, DEVICE_PERMANENTLY_UNAVAILABLE, CONCURRENCY_ERROR, INTERNAL_ERROR, PENDING_REQUEST_COUNT_EXCEEDS_LIMIT]
    """
    SUCCESS = "SUCCESS"
    INVALID_DEVICE = "INVALID_DEVICE"
    DEVICE_UNAVAILABLE = "DEVICE_UNAVAILABLE"
    DEVICE_PERMANENTLY_UNAVAILABLE = "DEVICE_PERMANENTLY_UNAVAILABLE"
    CONCURRENCY_ERROR = "CONCURRENCY_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    PENDING_REQUEST_COUNT_EXCEEDS_LIMIT = "PENDING_REQUEST_COUNT_EXCEEDS_LIMIT"

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
        if not isinstance(other, DispatchResultType):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (Any) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
