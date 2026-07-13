import logging
from base64 import b64encode
from http import HTTPStatus

import requests

from lucro_admin.infra.http.retry import RetryPolicy

logger = logging.getLogger('lucroadmin.adapters.bling')
retry_policy = RetryPolicy()


class Code:
    """
    Class for exchanging the code for longer-lived tokens,
    such as an Access Token and a Refresh Token.
    """

    def __init__(self):
        self.timeout = 30

    base_url: str = 'https://api.bling.com.br/Api/v3'

    def code_request(self, url, headers, data):
        """
        code_request
            Request para obtenção das credenciais bling.
            No retorno teremos as credênciais Access Token, Refresh Token e
            Expire

        :param self:
        :param url: Endpoint Bling
        :param headers: Headers para validação obtenção das credenciais
        :param data: Passando code em um Body
        """
        return requests.post(
            url=url, headers=headers, data=data, timeout=self.timeout
        )

    def generate_url_request(self, client_id: str, state: str) -> str:
        """
        generate_url_request
        Correctly constructs and formats the URL to which the request
        for obtaining tokens will be sent.

        :param self:
        :param client_id: Bling application credential
        :param state: Random state for response validation
        :return: URL (endpoint) for obtaining credentials
        """
        url: str = (
            f'{self.base_url}/oauth/authorize?response_type=code&'
            f'client_id={client_id}&state={state}'
        )
        logger.info('Bling oAuth Code | Constructed code request URL')
        return url

    def exchange_code_for_tokens(
        self, client_id: str, client_secret: str, code: str
    ):  # pyright: ignore[reportReturnType]
        """
        exchange_code_for_tokens
        Used to exchange the obtained code for credentials with
        a longer expiration time.

        :param self:
        :param client_id: Bling application credential
        :param client_secret: Bling application credential
        :param code: Token obtained through the manual authorization process
        """

        # Base64-encoded and separated by ":".
        to_64: str = f'{client_id}:{client_secret}'

        # Configuring credentials according to the Bling API documentation,
        base64_credentials: str = b64encode(to_64.encode('utf-8')).decode(
            'utf-8'
        )

        # Assembling headers and data for request submission
        headers: dict[str, str | int] = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {base64_credentials}',
            'enable-jwt': '1',
        }
        data: dict[str, str] = {
            'grant_type': 'authorization_code',
            'code': f'{code}'
        }

        url: str = f'{self.base_url}/oauth/token'
        logger.info(
            'Bling oAuth Code | Sending request to the endpoint %s', url
        )

        # Sending request to the endpoint
        response = retry_policy.executa(
            lambda: self.code_request(url, headers, data)
        )

        # Checking response
        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Bling oAuth Code | Request returned %s with CODE',
                response.status_code,
            )
            response_json = response.json()
            access: str = response_json['access_token']
            refresh: str = response_json['refresh_token']
            expire: int = response_json['expires_in']
            credentials = {
                'response_status_code': response.status_code,
                'access_token': access,
                'refresh_token': refresh,
                'expire': expire,
            }
            return credentials

        # Handling a temporary error
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning('Bling oAuth Code | Rate limit requests (429)')
            credentials = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 1,
            }
            return credentials
        # Critical request error, such as expired credentials or
        # invalid request
        else:
            logger.critical(
        'Bling oAuth Code | There was an error with the request. (%s) -> (%s)',
                response.status_code,
                response.text,
            )
            credentials = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 1,
            }
            return credenciais


class Refresh:
    """
    Exchange Refresh Token for a new Access Token.
    Validity periods:
    Refresh Token -> 30-day validity /
    Access Token -> 6 hours
    """

    def __init__(self):
        self.timeout = 30

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
        """
        refresh_access_token

        Configuring headers and data to exchange the Refresh Token for
        a new Access Token.

        :param self:
        :param client_id: Bling application credential
        :type client_id: str
        :param client_secret: Bling application credential
        :type client_secret: str
        :param refresh_token: Credential obtained via request that
        can be exchanged for a new access token when the current one expires.
        :type refresh_token: str
        """

        logger.info('Bling oAuth Refresh | Configuring credentials')
        url: str = 'https://api.bling.com.br/Api/v3/oauth/token'
        # Base64-encoded and separated by ":".
        to_64: str = f'{client_id}:{client_secret}'
        # Configurando credênciais conforme documentção da API Bling,

        base64_credentials: str = b64encode(to_64.encode('utf-8')).decode(
            'utf-8'
        )

        # Headers e Data for send Request
        headers: dict[str, str] = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {base64_credentials}',
            'enable-jwt': '1',
        }

        data: str = f'grant_type=refresh_token&refresh_token={refresh_token}'

        logger.info(
            'Bling oAuth Refresh | Headers and body assembled, sending request'
            ' to the endpoint %s',
            url,
        )

        response = retry_policy.executa(
            lambda: self.refresh_request(url=url, headers=headers, data=data)
        )
        # If the return is successful, we configure it according
        # to the established dataclass.
        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Bling oAuth Refresh | Returning %s for the request '
                'with the Refresh',
                response.status_code,
            )
            response_json = response.json()
            access: str = response_json['access_token']
            refresh: str = response_json['refresh_token']
            expire: int = response_json['expires_in']
            credentials = {
                'access_token': access,
                'refresh_token': refresh,
                'expire': expire,
                'response_status_code': response.status_code,
            }
            logger.info('Bling oAuth Refresh | Finish Request')
            return credentials

        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logging.warning(
                'Bling oAuth Refresh | Request limit, response %s',
                response.status_code,
            )
            credentials = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 1,
            }
            return credentials

        # Critical error: request configuration or credential failure.
        else:
            logger.critical(
            'Bling oAuth Refresh | A critical error occurred in the request'
                ' response %s -> %s',
                response.status_code,
                response.text,
            )
            credentials = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 1,
            }
            return credentials
