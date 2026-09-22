import logging
from http import HTTPStatus

import requests

from lucro_admin.infra.http.retry import RetryPolicy

logger = logging.getLogger('lucroadmin.adapters.tiny')
retry_policy = RetryPolicy()


class Code:

    def __init__(self):
        self.timeout = 30

    @retry_policy
    def code_request(self, url, headers, data):
        return requests.post(
            url=url, headers=headers, data=data, timeout=self.timeout
        )

    def exchange_code_for_tokens(  # noqa: PLR6301

            self,
            client_id: str,
            client_secret: str,
            redirect_uri: str,
            code: str,
    ):

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        # Assembling headers and data for request submission
        data = {
            'grant_type': 'authorization_code',
            'client_id': f'{client_id}',
            'client_secret': f'{client_secret}',
            'redirect_uri': f'{redirect_uri}',
            'code': f'{code}'
        }

        url = 'https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token'
        logger.info(
            'Tiny oAuth Code | Sending request to the endpoint %s', url
        )

        # Sending request to the endpoint
        response = self.code_request(url, headers, data)

        # Checking response
        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Tiny oAuth Code | Request returned %s with CODE',
                    response.status_code,
                    )
            response_json = response.json()
            access: str = response_json['access_token']
            expire_access: int = response_json['expires_in']
            refresh: str = response_json['refresh_token']
            expire_refresh = response_json['refresh_expires_in']
            state = response_json['session_state']
            credentials = {
                'response_status_code': response.status_code,
                'access_token': access,
                'expire_access': expire_access,
                'refresh_token': refresh,
                'expire_refresh': expire_refresh,
                'state': state
            }
            return credentials

        # Handling a temporary error
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning('Tiny oAuth Code | Rate limit requests (429)')
            credentials = {
                'response_status_code': response.status_code,
                'access_token': None,
                'expire_access': 1,
                'refresh_token': None,
                'expire_refresh': 1,
                'state': 'Error 429'
            }
            return credentials

        # Critical request error, such as expired credentials or
        # invalid request
        else:
            logger.critical(
        'Tiny oAuth Code | There was an error with the request. (%s) -> (%s)',
                response.status_code,
                response.text,
            )
            credentials = {
                'response_status_code': response.status_code,
                'access_token': None,
                'expire_access': 1,
                'refresh_token': None,
                'expire_refresh': 1,
                'state': 'Critical Error'
            }
            return credentials


class RefreshTiny:

    def __init__(self):
        self.timeout = 30

    @retry_policy
    def refresh_request(self, url: str, headers: dict[str, str], data: str):
        """
            refresh_request

            Uses the Refresh Token to obtain a new, valid Access Token.

            :param self:
            :param url: Credentials endpoint
            :type url: str
            :param header: Headers for credential validation/retrieval
            :type headers: dict[str, str]
            :param data: Refresh token passed in the request body
            :type data: str
            """
        return requests.post(
                url=url, headers=headers, data=data, timeout=self.timeout
        )

    def refresh_access_token(
            self, client_id: str, client_secret: str, refresh_token: str
        ):

        logger.info('Tiny oAuth Refresh | Configuring credentials')

        url = 'https://accounts.tiny.com.br/realms/tiny/protocol/openid-connect/token'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept':  'application/json'
        }

        data = {
            'grant_type': 'refresh_token',
            'client_id': f'{client_id}',
            'client_secret': f'{client_secret}',
            'refresh_token': f'{refresh_token}'
        }

        logger.info(
            'Tiny oAuth Refresh | Headers and body assembled, sending request'
            ' to the endpoint %s',
            url,
        )

        response = self.refresh_request(url=url, headers=headers, data=data)

        # If the return is successful, we configure it according
        # to the established dataclass.

        # Checking response
        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Tiny oAuth Code | Request returned %s with CODE',
                    response.status_code,
                    )
            response_json = response.json()
            access: str = response_json['access_token']
            expire_access: int = response_json['expires_in']
            refresh: str = response_json['refresh_token']
            expire_refresh = response_json['refresh_expires_in']
            state = response_json['session_state']
            credentials = {
                'response_status_code': response.status_code,
                'access_token': access,
                'expire_access': expire_access,
                'refresh_token': refresh,
                'expire_refresh': expire_refresh,
                'state': state
            }
            return credentials

        # Handling a temporary error
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning('Tiny oAuth Code | Rate limit requests (429)')
            credentials = {
                'response_status_code': response.status_code,
                'access_token': None,
                'expire_access': 1,
                'refresh_token': None,
                'expire_refresh': 1,
                'state': 'Error 429'
            }
            return credentials

        # Critical request error, such as expired credentials or
        # invalid request
        else:
            logger.critical(
        'Tiny oAuth Code | There was an error with the request. (%s) -> (%s)',
                response.status_code,
                response.text,
            )
            credentials = {
                'response_status_code': response.status_code,
                'access_token': None,
                'expire_access': 1,
                'refresh_token': None,
                'expire_refresh': 1,
                'state': 'Critical Error'
            }
            return credentials