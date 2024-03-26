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


class ListRuntimeErrorReason(Enum):
    """
    The reason for the failure.



    Allowed enum values: [INVALID_PRESENTATION_TOKEN, INVALID_LIST_ID, INVALID_DATASOURCE, INVALID_OPERATION, MISSING_LIST_VERSION, DUPLICATE_LIST_VERSION, LIST_INDEX_OUT_OF_RANGE, MISSING_LIST_VERSION_IN_SEND_DATA, LOAD_TIMEOUT, INCONSISTENT_LIST_ID, INCONSISTENT_PAGE_TOKEN, INCONSISTENT_PAGE_ITEMS, DUPLICATE_PAGE_TOKEN, OCCUPIED_LIST_INDEX, LOAD_INDEX_OUT_OF_RANGE, INCONSISTENT_RANGE, MISSING_LIST_ITEMS, INTERNAL_ERROR]
    """
    INVALID_PRESENTATION_TOKEN = "INVALID_PRESENTATION_TOKEN"
    INVALID_LIST_ID = "INVALID_LIST_ID"
    INVALID_DATASOURCE = "INVALID_DATASOURCE"
    INVALID_OPERATION = "INVALID_OPERATION"
    MISSING_LIST_VERSION = "MISSING_LIST_VERSION"
    DUPLICATE_LIST_VERSION = "DUPLICATE_LIST_VERSION"
    LIST_INDEX_OUT_OF_RANGE = "LIST_INDEX_OUT_OF_RANGE"
    MISSING_LIST_VERSION_IN_SEND_DATA = "MISSING_LIST_VERSION_IN_SEND_DATA"
    LOAD_TIMEOUT = "LOAD_TIMEOUT"
    INCONSISTENT_LIST_ID = "INCONSISTENT_LIST_ID"
    INCONSISTENT_PAGE_TOKEN = "INCONSISTENT_PAGE_TOKEN"
    INCONSISTENT_PAGE_ITEMS = "INCONSISTENT_PAGE_ITEMS"
    DUPLICATE_PAGE_TOKEN = "DUPLICATE_PAGE_TOKEN"
    OCCUPIED_LIST_INDEX = "OCCUPIED_LIST_INDEX"
    LOAD_INDEX_OUT_OF_RANGE = "LOAD_INDEX_OUT_OF_RANGE"
    INCONSISTENT_RANGE = "INCONSISTENT_RANGE"
    MISSING_LIST_ITEMS = "MISSING_LIST_ITEMS"
    INTERNAL_ERROR = "INTERNAL_ERROR"

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
        if not isinstance(other, ListRuntimeErrorReason):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (Any) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
