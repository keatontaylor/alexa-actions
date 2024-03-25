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

from ask_sdk_model.services.authentication_configuration import AuthenticationConfiguration
from ask_sdk_model.services.lwa.lwa_client import LwaClient


if typing.TYPE_CHECKING:
    from typing import Dict, List, Union, Any
    from datetime import datetime
    from ask_sdk_model.services.datastore.v1.commands_request_error import CommandsRequestError as CommandsRequestError_c6945312
    from ask_sdk_model.services.datastore.v1.commands_response import CommandsResponse as CommandsResponse_271f32fb
    from ask_sdk_model.services.datastore.v1.queued_result_response import QueuedResultResponse as QueuedResultResponse_806720cc
    from ask_sdk_model.services.datastore.v1.cancel_commands_request_error import CancelCommandsRequestError as CancelCommandsRequestError_26f4d59f
    from ask_sdk_model.services.datastore.v1.commands_request import CommandsRequest as CommandsRequest_4046908d
    from ask_sdk_model.services.datastore.v1.queued_result_request_error import QueuedResultRequestError as QueuedResultRequestError_fc34ffb1


class DatastoreServiceClient(BaseServiceClient):
    """ServiceClient for calling the DatastoreService APIs.

    :param api_configuration: Instance of ApiConfiguration
    :type api_configuration: ask_sdk_model.services.api_configuration.ApiConfiguration
    """
    def __init__(self, api_configuration, authentication_configuration, lwa_client=None, custom_user_agent=None):
        # type: (ApiConfiguration, AuthenticationConfiguration, LwaClient, str) -> None
        """
        :param api_configuration: Instance of :py:class:`ask_sdk_model.services.api_configuration.ApiConfiguration`
        :type api_configuration: ask_sdk_model.services.api_configuration.ApiConfiguration
        :param authentication_configuration: Instance of :py:class:`ask_sdk_model.services.authentication_configuration.AuthenticationConfiguration`
        :type api_configuration: ask_sdk_model.services.authentication_configuration.AuthenticationConfiguration
        :param lwa_client: (Optional) Instance of :py:class:`ask_sdk_model.services.lwa.LwaClient`,
            can be passed when the LwaClient configuration is different from the authentication 
            and api configuration passed
        :type lwa_client: ask_sdk_model.services.lwa.LwaClient
        :param custom_user_agent: Custom User Agent string provided by the developer.
        :type custom_user_agent: str
        """
        super(DatastoreServiceClient, self).__init__(api_configuration)
        self.user_agent = user_agent_info(sdk_version="1.0.0", custom_user_agent=custom_user_agent)

        if lwa_client is None:
            self._lwa_service_client = LwaClient(
                api_configuration=ApiConfiguration(
                    serializer=api_configuration.serializer, 
                    api_client=api_configuration.api_client),
                authentication_configuration=authentication_configuration,
                grant_type=None)
        else:
            self._lwa_service_client = lwa_client

    def commands_v1(self, commands_request, **kwargs):
        # type: (CommandsRequest_4046908d, **Any) -> Union[ApiResponse, object, CommandsResponse_271f32fb, CommandsRequestError_c6945312]
        """
        Send DataStore commands to Alexa device.

        :param commands_request: (required) 
        :type commands_request: ask_sdk_model.services.datastore.v1.commands_request.CommandsRequest
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, CommandsResponse_271f32fb, CommandsRequestError_c6945312]
        """
        operation_name = "commands_v1"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'commands_request' is set
        if ('commands_request' not in params) or (params['commands_request'] is None):
            raise ValueError(
                "Missing the required parameter `commands_request` when calling `" + operation_name + "`")

        resource_path = '/v1/datastore/commands'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict

        query_params = []  # type: List

        header_params = []  # type: List

        body_params = None
        if 'commands_request' in params:
            body_params = params['commands_request']
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        access_token = self._lwa_service_client.get_access_token_for_scope(
            "alexa::datastore")
        authorization_value = "Bearer " + access_token
        header_params.append(('Authorization', authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.commands_response.CommandsResponse", status_code=200, message="Multiple CommandsDispatchResults in response."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.commands_request_error.CommandsRequestError", status_code=400, message="Request validation fails."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.commands_request_error.CommandsRequestError", status_code=401, message="Not Authorized."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.commands_request_error.CommandsRequestError", status_code=403, message="The skill is not allowed to execute commands."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.commands_request_error.CommandsRequestError", status_code=429, message="The client has made more calls than the allowed limit."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.commands_request_error.CommandsRequestError", status_code=0, message="Unexpected error."))

        api_response = self.invoke(
            method="POST",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.datastore.v1.commands_response.CommandsResponse")

        if full_response:
            return api_response
        return api_response.body
        

    def cancel_commands_v1(self, queued_result_id, **kwargs):
        # type: (str, **Any) -> Union[ApiResponse, object, CancelCommandsRequestError_26f4d59f]
        """
        Cancel pending DataStore commands.

        :param queued_result_id: (required) A unique identifier to query result for queued delivery for offline devices (DEVICE_UNAVAILABLE).
        :type queued_result_id: str
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, CancelCommandsRequestError_26f4d59f]
        """
        operation_name = "cancel_commands_v1"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'queued_result_id' is set
        if ('queued_result_id' not in params) or (params['queued_result_id'] is None):
            raise ValueError(
                "Missing the required parameter `queued_result_id` when calling `" + operation_name + "`")

        resource_path = '/v1/datastore/queue/{queuedResultId}/cancel'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'queued_result_id' in params:
            path_params['queuedResultId'] = params['queued_result_id']

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
        access_token = self._lwa_service_client.get_access_token_for_scope(
            "alexa::datastore")
        authorization_value = "Bearer " + access_token
        header_params.append(('Authorization', authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type=None, status_code=204, message="Success. No content."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.cancel_commands_request_error.CancelCommandsRequestError", status_code=400, message="Request validation fails."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.cancel_commands_request_error.CancelCommandsRequestError", status_code=401, message="Not Authorized."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.cancel_commands_request_error.CancelCommandsRequestError", status_code=403, message="The skill is not allowed to call this API commands."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.cancel_commands_request_error.CancelCommandsRequestError", status_code=404, message="Unable to find the pending request."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.cancel_commands_request_error.CancelCommandsRequestError", status_code=429, message="The client has made more calls than the allowed limit."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.cancel_commands_request_error.CancelCommandsRequestError", status_code=0, message="Unexpected error."))

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

    def queued_result_v1(self, queued_result_id, **kwargs):
        # type: (str, **Any) -> Union[ApiResponse, object, QueuedResultResponse_806720cc, QueuedResultRequestError_fc34ffb1]
        """
        Query statuses of deliveries to offline devices returned by commands API.

        :param queued_result_id: (required) A unique identifier to query result for queued delivery for offline devices (DEVICE_UNAVAILABLE).
        :type queued_result_id: str
        :param max_results: Maximum number of CommandsDispatchResult items to return.
        :type max_results: int
        :param next_token: The value of nextToken in the response to fetch next page. If not specified, the request fetches result for the first page. 
        :type next_token: str
        :param full_response: Boolean value to check if response should contain headers and status code information.
            This value had to be passed through keyword arguments, by default the parameter value is set to False. 
        :type full_response: boolean
        :rtype: Union[ApiResponse, object, QueuedResultResponse_806720cc, QueuedResultRequestError_fc34ffb1]
        """
        operation_name = "queued_result_v1"
        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'queued_result_id' is set
        if ('queued_result_id' not in params) or (params['queued_result_id'] is None):
            raise ValueError(
                "Missing the required parameter `queued_result_id` when calling `" + operation_name + "`")

        resource_path = '/v1/datastore/queue/{queuedResultId}'
        resource_path = resource_path.replace('{format}', 'json')

        path_params = {}  # type: Dict
        if 'queued_result_id' in params:
            path_params['queuedResultId'] = params['queued_result_id']

        query_params = []  # type: List
        if 'max_results' in params:
            query_params.append(('maxResults', params['max_results']))
        if 'next_token' in params:
            query_params.append(('nextToken', params['next_token']))

        header_params = []  # type: List

        body_params = None
        header_params.append(('Content-type', 'application/json'))
        header_params.append(('User-Agent', self.user_agent))

        # Response Type
        full_response = False
        if 'full_response' in params:
            full_response = params['full_response']

        # Authentication setting
        access_token = self._lwa_service_client.get_access_token_for_scope(
            "alexa::datastore")
        authorization_value = "Bearer " + access_token
        header_params.append(('Authorization', authorization_value))

        error_definitions = []  # type: List
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.queued_result_response.QueuedResultResponse", status_code=200, message="Unordered array of CommandsDispatchResult and pagination details."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.queued_result_request_error.QueuedResultRequestError", status_code=400, message="Request validation fails."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.queued_result_request_error.QueuedResultRequestError", status_code=401, message="Not Authorized."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.queued_result_request_error.QueuedResultRequestError", status_code=403, message="The skill is not allowed to call this API commands."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.queued_result_request_error.QueuedResultRequestError", status_code=429, message="The client has made more calls than the allowed limit."))
        error_definitions.append(ServiceClientResponse(response_type="ask_sdk_model.services.datastore.v1.queued_result_request_error.QueuedResultRequestError", status_code=0, message="Unexpected error."))

        api_response = self.invoke(
            method="GET",
            endpoint=self._api_endpoint,
            path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            response_definitions=error_definitions,
            response_type="ask_sdk_model.services.datastore.v1.queued_result_response.QueuedResultResponse")

        if full_response:
            return api_response
        return api_response.body
        
