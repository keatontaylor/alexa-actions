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
from ask_sdk_model.interfaces.geolocation.geolocation_common_state import GeolocationCommonState


if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Union, Any
    from datetime import datetime
    from ask_sdk_model.interfaces.geolocation.altitude import Altitude as Altitude_328a6962
    from ask_sdk_model.interfaces.geolocation.heading import Heading as Heading_bf10e3ca
    from ask_sdk_model.interfaces.geolocation.speed import Speed as Speed_22d2d794
    from ask_sdk_model.interfaces.geolocation.coordinate import Coordinate as Coordinate_c6912a2
    from ask_sdk_model.interfaces.geolocation.location_services import LocationServices as LocationServices_c8dfc485


class GeolocationState(GeolocationCommonState):
    """
    The geolocation object used in the Context of API


    :param timestamp: Specifies the time when the geolocation data was last collected on the device.
    :type timestamp: (optional) str
    :param coordinate: 
    :type coordinate: (optional) ask_sdk_model.interfaces.geolocation.coordinate.Coordinate
    :param altitude: 
    :type altitude: (optional) ask_sdk_model.interfaces.geolocation.altitude.Altitude
    :param heading: 
    :type heading: (optional) ask_sdk_model.interfaces.geolocation.heading.Heading
    :param speed: 
    :type speed: (optional) ask_sdk_model.interfaces.geolocation.speed.Speed
    :param location_services: 
    :type location_services: (optional) ask_sdk_model.interfaces.geolocation.location_services.LocationServices

    """
    deserialized_types = {
        'timestamp': 'str',
        'coordinate': 'ask_sdk_model.interfaces.geolocation.coordinate.Coordinate',
        'altitude': 'ask_sdk_model.interfaces.geolocation.altitude.Altitude',
        'heading': 'ask_sdk_model.interfaces.geolocation.heading.Heading',
        'speed': 'ask_sdk_model.interfaces.geolocation.speed.Speed',
        'location_services': 'ask_sdk_model.interfaces.geolocation.location_services.LocationServices'
    }  # type: Dict

    attribute_map = {
        'timestamp': 'timestamp',
        'coordinate': 'coordinate',
        'altitude': 'altitude',
        'heading': 'heading',
        'speed': 'speed',
        'location_services': 'locationServices'
    }  # type: Dict
    supports_multiple_types = False

    def __init__(self, timestamp=None, coordinate=None, altitude=None, heading=None, speed=None, location_services=None):
        # type: (Optional[str], Optional[Coordinate_c6912a2], Optional[Altitude_328a6962], Optional[Heading_bf10e3ca], Optional[Speed_22d2d794], Optional[LocationServices_c8dfc485]) -> None
        """The geolocation object used in the Context of API

        :param timestamp: Specifies the time when the geolocation data was last collected on the device.
        :type timestamp: (optional) str
        :param coordinate: 
        :type coordinate: (optional) ask_sdk_model.interfaces.geolocation.coordinate.Coordinate
        :param altitude: 
        :type altitude: (optional) ask_sdk_model.interfaces.geolocation.altitude.Altitude
        :param heading: 
        :type heading: (optional) ask_sdk_model.interfaces.geolocation.heading.Heading
        :param speed: 
        :type speed: (optional) ask_sdk_model.interfaces.geolocation.speed.Speed
        :param location_services: 
        :type location_services: (optional) ask_sdk_model.interfaces.geolocation.location_services.LocationServices
        """
        self.__discriminator_value = None  # type: str

        super(GeolocationState, self).__init__(timestamp=timestamp, coordinate=coordinate, altitude=altitude, heading=heading, speed=speed)
        self.location_services = location_services

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
        if not isinstance(other, GeolocationState):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
