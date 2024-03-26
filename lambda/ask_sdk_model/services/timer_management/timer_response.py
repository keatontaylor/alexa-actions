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
    from ask_sdk_model.services.timer_management.status import Status as Status_26679d1d


class TimerResponse(object):
    """
    Timer object


    :param id: Unique id of this timer alert
    :type id: (optional) str
    :param status: 
    :type status: (optional) ask_sdk_model.services.timer_management.status.Status
    :param duration: An ISO-8601 representation of duration. E.g. for 2 minutes and 3 seconds - \&quot;PT2M3S\&quot;.
    :type duration: (optional) str
    :param trigger_time: Valid ISO 8601 format - Trigger time of this timer alert.
    :type trigger_time: (optional) datetime
    :param timer_label: Label of this timer alert, maximum of 256 character.
    :type timer_label: (optional) str
    :param created_time: Valid ISO 8601 format - Creation time of this timer alert.
    :type created_time: (optional) datetime
    :param updated_time: Valid ISO 8601 format - Last updated time of this timer alert.
    :type updated_time: (optional) datetime
    :param remaining_time_when_paused: An ISO-8601 representation of duration remaining since the timer was last paused. E.g. for 1 hour, 3 minutes and 31 seconds - \&quot;PT1H3M31S\&quot;.
    :type remaining_time_when_paused: (optional) str

    """
    deserialized_types = {
        'id': 'str',
        'status': 'ask_sdk_model.services.timer_management.status.Status',
        'duration': 'str',
        'trigger_time': 'datetime',
        'timer_label': 'str',
        'created_time': 'datetime',
        'updated_time': 'datetime',
        'remaining_time_when_paused': 'str'
    }  # type: Dict

    attribute_map = {
        'id': 'id',
        'status': 'status',
        'duration': 'duration',
        'trigger_time': 'triggerTime',
        'timer_label': 'timerLabel',
        'created_time': 'createdTime',
        'updated_time': 'updatedTime',
        'remaining_time_when_paused': 'remainingTimeWhenPaused'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, id=None, status=None, duration=None, trigger_time=None, timer_label=None, created_time=None, updated_time=None, remaining_time_when_paused=None):
        # type: (Optional[str], Optional[Status_26679d1d], Optional[str], Optional[datetime], Optional[str], Optional[datetime], Optional[datetime], Optional[str]) -> None
        """Timer object

        :param id: Unique id of this timer alert
        :type id: (optional) str
        :param status: 
        :type status: (optional) ask_sdk_model.services.timer_management.status.Status
        :param duration: An ISO-8601 representation of duration. E.g. for 2 minutes and 3 seconds - \&quot;PT2M3S\&quot;.
        :type duration: (optional) str
        :param trigger_time: Valid ISO 8601 format - Trigger time of this timer alert.
        :type trigger_time: (optional) datetime
        :param timer_label: Label of this timer alert, maximum of 256 character.
        :type timer_label: (optional) str
        :param created_time: Valid ISO 8601 format - Creation time of this timer alert.
        :type created_time: (optional) datetime
        :param updated_time: Valid ISO 8601 format - Last updated time of this timer alert.
        :type updated_time: (optional) datetime
        :param remaining_time_when_paused: An ISO-8601 representation of duration remaining since the timer was last paused. E.g. for 1 hour, 3 minutes and 31 seconds - \&quot;PT1H3M31S\&quot;.
        :type remaining_time_when_paused: (optional) str
        """
        self.__discriminator_value = None  # type: str

        self.id = id
        self.status = status
        self.duration = duration
        self.trigger_time = trigger_time
        self.timer_label = timer_label
        self.created_time = created_time
        self.updated_time = updated_time
        self.remaining_time_when_paused = remaining_time_when_paused

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
        if not isinstance(other, TimerResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
