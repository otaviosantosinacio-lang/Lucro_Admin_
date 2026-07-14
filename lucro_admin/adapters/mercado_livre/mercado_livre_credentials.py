import logging
from http import HTTPStatus

import requests

from lucro_admin.infra.http.retry import RetryPolicy

logger = logging.getLogger('lucroadmin.adapters.mercadolivre')
retry_policy = RetryPolicy()

base_url: str = 'https://api.mercadolibre.com/oauth/token'


class Code:
    def __init__(self):
        self.timeout = 30

    def code_request(self, headers, data) -> requests.Response:

        return requests.post(
            url=base_url, headers=headers, data=data, timeout=self.timeout
        )

    def exchange_code_for_tokens(
        self, client_id: str,
        client_secret: str, code: str,
        redirect_url: str
    ):

        logger.info(
            'Mercado Livre oAuth Code | Starting to set up headers and body'

        )
        headers: dict[str, str] = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data: dict[str, str] = {
            'grant_type': 'authorization_code',
            'client_id': f'{client_id}',
            'client_secret': f'{client_secret}',
            'code': f'{code}',
            'redirect_uri': f'{redirect_url}'
        }

        logger.info(
            'Mercado Livre oAuth Code | Sending a request to the endpoint %s',
            base_url,
        )

        response = retry_policy.executa(
            lambda: self.code_request(headers, data)
        )

        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Mercado Lvire oAuth Code | Return %s of the request with CODE',
                response.status_code,
            )
            response_json = response.json()
            access: str = response_json['access_token']
            refresh: str = response_json['refresh_token']
            expire: int = response_json['expires_in']
            credencial = {
                'response_status_code': response.status_code,
                'access_token': access,
                'refresh_token': refresh,
                'expire': expire,
            }
            return credencial

        # Handling temporary error
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning(
                'Mercado Livre oAuth Code | Limit that requests (429)'
            )
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': None,
                'refresh_token': None,
                'expire': 100,
            }
            return credenciais

        # Critical error in the request like expired credentials or invalid
        # request
        else:
            logger.critical(
                'Mercado Livre oAuth Code | THERE WAS AN ERROR IN THE REQUEST'
                ' (%s) -> (%s)',
                response.status_code,
                response.text,
            )
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': None,
                'refresh_token': None,
                'expire': 100,
            }
            return credenciais


class RefreshML:
    def __init__(self):
        self.timeout = 20

    def refresh_request(
        self, url: str, headers: dict[str, str], data: str
    ) -> requests.Response:

        return requests.post(
            url=url, headers=headers, data=data, timeout=self.timeout
        )

    def using_refresh_token(
        self, client_id: str, client_secret: str, refresh_token: str
    ):

        logger.info(
            'Mercado Livre oAuth Refresh | Setting up the credentials'
        )

        headers: dict[str, str] = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data: dict[str, str] = {
            'grant_type': 'refresh_token',
            'client_id': f'{client_id}',
            'client_secret': f'{client_secret}',
            'refresh_token': f'{refresh_token}'
        }

        logger.info(
            'Mercado Livre oAuth Refresh | Headers and body set up, sending'
            ' request to the endpoint %s',
            base_url,
        )

        response = retry_policy.executa(
            lambda: self.refresh_request(
                url=base_url, headers=headers, data=data
            )
        )

        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Mercado Livre  oAuth Refresh | Return %s for the request'
                ' with the Refresh',
                response.status_code,
            )
            response_json = response.json()
            access: str = response_json['access_token']
            refresh: str = response_json['refresh_token']
            expire: int = response_json['expires_in']
            credenciais = {
                'access_token': access,
                'refresh_token': refresh,
                'expire': expire,
                'response_status_code': response.status_code,
            }
            logger.info('Mercado Livre oAuth Refresh | Request finished')
            return credenciais

        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logging.warning(
                'Mercado Livre oAuth Refresh | Request return limit %s',
                response.status_code,
            )
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 1,
            }
            return credenciais

        # Erro critico de falha na configuração do request ou até credênciais
        else:
            logger.critical(
                'Mercado Livre oAuth Refresh | There was a critical error in'
                ' the return request %s -> %s',
                response.status_code,
                response.text,
            )
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 100,
            }
            return credenciais
