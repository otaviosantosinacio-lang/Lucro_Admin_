import logging
from base64 import b64encode
from http import HTTPStatus

import requests

from lucro_admin.infra.http.retry import RetryPolicy

logger = logging.getLogger('lucroadmin.adapters.bling')
retry_policy = RetryPolicy()


class Code:
    """
    Class para trocarmos o code por Tokens de maior duração como Access Token
    e Refresh Token

    """

    base_url: str = 'https://www.bling.com.br/Api/v3'

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
        return requests.post(url=url, headers=headers, data=data, timeout=20)

    def gerando_url_request(self, client_id: str, state: str) -> str:
        """
        gerando_url_request
        Montagem correta e formatada da url onde será enviada a requisição
        para obtenção dos tokens.

        :param self:
        :param client_id: Credencial do aplicativo Bling
        :param state: State aleátorio para validação do retorno
        :return: URL (end point)para obtenção das credenciais
        """
        url: str = (
            f'{self.base_url}/oauth/authorize?response_type=code&'
            f'client_id={client_id}&state={state}'
        )
        logger.info('Bling oAuth Code | URL de requisição do code montada')
        return url

    def troca_code_por_tokens(
        self, client_id: str, client_secret: str, code: str
    ):  # pyright: ignore[reportReturnType]
        """
        troca_code_por_tokens
        Utilizada para através do code obtido trocarmos por credênciais de
        maior tempo de expiração.

        :param self:
        :param client_id: Credencial do aplicativo Bling
        :param client_secret: Credencial do aplicativo Bling
        :param code: Token obtido através do processo de autorização manual
        """

        para64: str = f'{client_id}:{client_secret}'
        # Configurando credênciais conforme documentação da api bling,
        # codificadas em base64 separadas por ":".
        credenciaisbase64: str = b64encode(para64.encode('utf-8')).decode(
            'utf-8'
        )

        # Montagem de headers e data para envio request
        headers: dict[str, str | int] = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {credenciaisbase64}',
            'enable-jwt': '1',
        }
        data: str = f'grant_type=authorization_code&code={code}'

        url: str = f'{self.base_url}/oauth/token'
        logger.info(
            'Bling oAuth Code | Enviando requisição para o endpoint %s', url
        )

        # Enviando requisição para o endpoint
        response = retry_policy.executa(
            lambda: self.code_request(url, headers, data)
        )

        # Verificando o retorno
        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Bling oAuth Code | Retorno %s da requisição com CODE',
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
            logger.warning('Bling oAuth Code | Limite que requisições (429)')
            credenciais = {
                'response_status_code': response.status_code,
                'access_token': '',
                'refresh_token': '',
                'expire': 100,
            }
            return credenciais
        # Erro crítico na requisição como credênciais expiradas ou
        # request inválido
        else:
            logger.critical(
                'Bling oAuth Code | HOUVE UM ERRO NA REQUISIÇÃO (%s) -> (%s)',
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


class Refresh:
    """
    Toca de Refresh Token por um novo Access Token
    Validades:
    Refresh Token -> Validade de 30 dias
    Access Token -> 6 horas

    """

    def refresh_request(self, url: str, headers: dict[str, str], data: str):
        """
        refresh_request
        Utilizando o Refresh Token para obter um novo Access Token válido.
        :param self:
        :param url: EndPoint das credênciais
        :type url: str
        :param header: Headers para validação obtenção das credenciais
        :type headers: dict[str, str]
        :param data: Passando Refresh em um Body
        :type data: stR
        """
        return requests.post(url=url, headers=headers, data=data, timeout=20)

    def usando_refresh_token(
        self, client_id: str, client_secret: str, refresh_token: str
    ):
        """
        usando_refresh_token

        Configurando headers e data para trocar o Refresh Token por
        um novo Access Token.

        :param self:
        :param client_id: Credecial do aplicativo Bling
        :type client_id: str
        :param client_secret: Credencial do aplicativo Bling
        :type client_secret: str
        :param refresh_token: Credencial obtida atráves de request e
        pode ser trocada por um novo access token quando o mesmo expira.
        :type refresh_token: str
        """

        logger.info('Bling oAuth Refresh | Configurando as credenciais')
        url: str = 'https://www.bling.com.br/Api/v3/oauth/token'
        para64: str = f'{client_id}:{client_secret}'
        # Configurando credênciais conforme documentção da API Bling,
        # codificadas em base64 e separadas por ":"
        credenciaisbase64: str = b64encode(para64.encode('utf-8')).decode(
            'utf-8'
        )

        # Headers e Data para envio de Request
        headers: dict[str, str] = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {credenciaisbase64}',
            'enable_jwt': '1',
        }

        data: str = f'grant_type=refresh_token&refresh_token={refresh_token}'

        logger.info(
            'Bling oAuth Refresh | Headers e Body montado, enviando requisição'
            ' para o endpoint %s',
            url,
        )

        response = retry_policy.executa(
            lambda: self.refresh_request(url=url, headers=headers, data=data)
        )

        # Retorno sendo sucesso configuramos ele conforme dataclass
        #  estabelecido
        if response.status_code == HTTPStatus.OK:
            logger.info(
                'Bling oAuth Refresh | Retorno %s para a requisição '
                'com o Refresh',
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
            logger.info('Bling oAuth Refresh | Request finalizado')
            return credenciais

        # Sendo um retorno também configrado para tratarmos ele
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logging.warning(
                'Bling oAuth Refresh | Limite de requisições retorno %s',
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
                'Bling oAuth Refresh | Houve um erro critico na requisição'
                ' retorno %s -> %s',
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
