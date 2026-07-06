import logging

import requests

from lucro_admin.infra.http.retry import RetryPolicy

retry_policy = RetryPolicy()
logger = logging.getLogger('lucroadmin.adapters.mercadolivre')


class RequestMercadoPago:
    def __init__(self):
        self.time_out = 20

    def request_endpoint(self, url: str, headers: dict[str, str]):

        logger.info(
            'Mercado Pago Request | Enviando requisição para o end point %s',
            url,
        )
        response = requests.get(
            url=url, headers=headers, timeout=self.time_out
        )

        return response


class GetMercadoPago:

    def __init__(self):
        self.request_mp = RequestMercadoPago()

    def get_endpoint(self, access_token: str, url: str):
        """
        :param self: Objeto
        :param access_token: Credencial de acesso válida
        :type access_token: string
        :param url: Endpoint Mercado Livre
        :type url: String

        Headers e request para endpoint Mercado Livre para retornar ao
        service o json.
        """
        logger.info(
            'Mercado Pago get_endpoints_mercadopago | Iniciando o Request'
        )
        headers: dict[str, str] = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        response = retry_policy.executa(
            lambda: self.request_mp.request_endpoint(url, headers)
        )
        logger.info(
            'Bling get_endpoints_bling | Retorno da requisição é %s',
            response.status_code,
        )

        return response
