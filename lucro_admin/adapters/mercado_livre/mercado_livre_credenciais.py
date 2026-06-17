import logging
from http import HTTPStatus

import requests

from lucro_admin.infra.http.retry import RetryPolicy

logger = logging.getLogger('lucroadmin.adapters.mercadolivre')
retry_policy = RetryPolicy()

base_url: str = 'https://api.mercadolibre.com/oauth/token'


class Code:
    def code_request(self, headers, data) -> requests.Response:

        return requests.post(
            url=base_url, headers=headers, data=data, timeout=20
        )

    def troca_code_por_tokens(
        self, client_id: str, client_secret: str, code: str, redirect_url: str
    ):

        logger.info(
            'Mercado Livre oAuth Code | Iniciando montagem de '
            'cabeçalhos e body'
        )
        headers: dict[str, str] = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data = str(
            f'grant_type=authorization_code'
            f'&client_id={client_id}'
            f'&client_secret={client_secret}'
            f'&code={code}'
            f'&redirect_uri={redirect_url}'
        )

        logger.info(
            'Mercado Livre oAuth Code | Enviando requisição para '
            'o endpoint %s',
            base_url,
        )

        response = retry_policy.executa(
            lambda: self.code_request(headers, data)
        )

        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Mercado Lvire oAuth Code | Retorno %s da requisição com CODE',
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

        # Tratanto erro temporário
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.warning(
                'Mercado Livre oAuth Code | Limite que requisições (429)'
            )
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 100,
            }
            return credenciais

        # Erro crítico na requisição como credênciais expiradas ou request
        # inválido
        else:
            logger.critical(
                'Mercado Livre oAuth Code | HOUVE UM ERRO NA REQUISIÇÃO '
                '(%s) -> (%s)',
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


class RefreshML:
    def refresh_request(
        self, url: str, headers: dict[str, str], data: str
    ) -> requests.Response:

        return requests.post(url=url, headers=headers, data=data, timeout=20)

    def usando_refresh_token(
        self, client_id: str, client_secret: str, refresh_token: str
    ):

        logger.info(
            'Mercado Livre oAuth Refresh | Configurando as credenciais'
        )

        headers: dict[str, str] = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data = str(
            f'grant_type=refresh_token'
            f'&client_id={client_id}'
            f'&client_secret={client_secret}'
            f'&refresh_token={refresh_token}'
        )

        logger.info(
            'Mercado Livre oAuth Refresh | Headers e Body montado, enviando '
            'requisição para o endpoint %s',
            base_url,
        )

        response = retry_policy.executa(
            lambda: self.refresh_request(
                url=base_url, headers=headers, data=data
            )
        )

        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Mercado Livre  oAuth Refresh | Retorno %s para a requisição'
                ' com o Refresh',
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
            logger.info('Mercado Livre oAuth Refresh | Request finalizado')
            return credenciais
        # Sendo um retorno também configrado para tratarmos ele

        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logging.warning(
                'Mercado Livre oAuth Refresh | Limite de requisições '
                'retorno %s',
                response.status_code,
            )
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 100,
            }
            return credenciais

        # Erro critico de falha na configuração do request ou até credênciais
        else:
            logger.critical(
                'Mercado Livre oAuth Refresh | Houve um erro critico na'
                ' requisição retorno %s -> %s',
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
