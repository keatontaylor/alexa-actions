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

import sys
import os
import re
import six
import typing

from ask_sdk_model.services.base_service_client import BaseServiceClient
from ask_sdk_model.services.api_configuration import ApiConfiguration
from ask_sdk_model.services.service_client_response import ServiceClientResponse
from ask_sdk_model.services.api_response import ApiResponse
from ask_sdk_model.services.utils import user_agent_info



if typing.TYPE_CHECKING:
    from typing import Dict, List, Union, Any
    from datetime import datetime
    from ask_sdk_model.services.timer_management.timers_response import TimersResponse as TimersResponse_df2de7c
    from ask_sdk_model.services.timer_management.timer_request import TimerRequest as TimerRequest_5f036a34
    from ask_sdk_model.services.timer_management.error import Error as Error_249911d1
    from ask_sdk_model.services.timer_management.timer_response import TimerResponse as TimerResponse_5be9ee64


class TimerManagementServiceClient(BaseServiceClient):
    """ServiceClient for calling the TimerManagementService APIs.

    :param api_configuration: Instance of ApiConfiguration
    :type api_configuration: ask_sdk_model.services.api_configuration.ApiConfiguration
    """
    def __init__(self, api_configuration, custom_user_agent=None):
        # type: (ApiConfiguration, str) -> None
        """
        :param api_configuration: Instance of :py:class:`ask_sdk_model.services.api_configuration.ApiConfiguration`
        :type api_configuration: ask_sdk_model.services.api_configuration.ApiConfiguration
        :param custom_user_agent: Custom User Agent string provided by the developer.
        :type custom_user_agent: str
        """
        super(TimerManagementServiceClient, self).__init__(api_configuration)
        self.user_agent = user_agent_info(sdk_version="1.0.0", custom_user_agent=custom_user_agent)

    def delete_timers(self, **kwargs):
        # type: (**Any) -> Union[ApiResponse, object, Error_249911d1]
        """
        Delete all timers created by the skill. 

        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, Error_249911d1]
        """
        operation_name = "delete_timers"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']

        resource_path = '/v1/alerts/timers'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))

        api_response = self.invoke(
            method="DELETE",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type=None)

        if full_response:
            return api_response
        
        return None

    def get_timers(self, **kwargs):
        # type: (**Any) -> Union[ApiResponse, object, TimersResponse_df2de7c, Error_249911d1]
        """
        Get all timers created by the skill. 

        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, TimersResponse_df2de7c, Error_249911d1]
        """
        operation_name = "get_timers"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']

        resource_path = '/v1/alerts/timers'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.timers_response.TimersResponse", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))

        api_response = self.invoke(
            method="GET",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.timer_management.timers_response.TimersResponse")

        if full_response:
            return api_response
        return api_response.body
        

    def delete_timer(self, id, **kwargs):
        # type: (str, **Any) -> Union[ApiResponse, object, Error_249911d1]
        """
        Delete a timer by ID. 

        :param id: (required) 
        :type id: str
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, Error_249911d1]
        """
        operation_name = "delete_timer"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError(
                "Missing the required parameter `id` when calling `" + operation_name + "`")

        resource_path = '/v1/alerts/timers/{id}'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=404, message="Timer not found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))

        api_response = self.invoke(
            method="DELETE",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type=None)

        if full_response:
            return api_response
        
        return None

    def get_timer(self, id, **kwargs):
        # type: (str, **Any) -> Union[ApiResponse, object, TimerResponse_5be9ee64, Error_249911d1]
        """
        Get timer by ID. 

        :param id: (required) 
        :type id: str
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, TimerResponse_5be9ee64, Error_249911d1]
        """
        operation_name = "get_timer"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError(
                "Missing the required parameter `id` when calling `" + operation_name + "`")

        resource_path = '/v1/alerts/timers/{id}'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.timer_response.TimerResponse", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=404, message="Timer not found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))

        api_response = self.invoke(
            method="GET",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.timer_management.timer_response.TimerResponse")

        if full_response:
            return api_response
        return api_response.body
        

    def pause_timer(self, id, **kwargs):
        # type: (str, **Any) -> Union[ApiResponse, object, Error_249911d1]
        """
        Pause a timer. 

        :param id: (required) 
        :type id: str
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, Error_249911d1]
        """
        operation_name = "pause_timer"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError(
                "Missing the required parameter `id` when calling `" + operation_name + "`")

        resource_path = '/v1/alerts/timers/{id}/pause'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=404, message="Timer not found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=504, message="Device offline"))

        api_response = self.invoke(
            method="POST",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type=None)

        if full_response:
            return api_response
        
        return None

    def resume_timer(self, id, **kwargs):
        # type: (str, **Any) -> Union[ApiResponse, object, Error_249911d1]
        """
        Resume a timer. 

        :param id: (required) 
        :type id: str
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, Error_249911d1]
        """
        operation_name = "resume_timer"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError(
                "Missing the required parameter `id` when calling `" + operation_name + "`")

        resource_path = '/v1/alerts/timers/{id}/resume'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=404, message="Timer not found"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=504, message="Device offline"))

        api_response = self.invoke(
            method="POST",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type=None)

        if full_response:
            return api_response
        
        return None

    def create_timer(self, timer_request, **kwargs):
        # type: (TimerRequest_5f036a34, **Any) -> Union[ApiResponse, object, TimerResponse_5be9ee64, Error_249911d1]
        """
        Create a new timer. 

        :param timer_request: (required) 
        :type timer_request: ask_sdk_model.services.timer_management.timer_request.TimerRequest
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, TimerResponse_5be9ee64, Error_249911d1]
        """
        operation_name = "create_timer"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'timer_request' is set
        if ('timer_request' not in params) or (params['timer_request'] is None):
            raise ValueError(
                "Missing the required parameter `timer_request` when calling `" + operation_name + "`")

        resource_path = '/v1/alerts/timers'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        if 'timer_request' in params:
            body_params = params['timer_request']
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        authorization_value = "Bearer " + self._authorization_value
        header_params.append(("Authorization", authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.timer_response.TimerResponse", status_code=200, message="Success"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=400, message="Bad Request"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=401, message="Unauthorized"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=403, message="Forbidden"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=500, message="Internal Server Error"))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.timer_management.error.Error", status_code=504, message="Device offline"))

        api_response = self.invoke(
            method="POST",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.timer_management.timer_response.TimerResponse")

        if full_response:
            return api_response
        return api_response.body
        
