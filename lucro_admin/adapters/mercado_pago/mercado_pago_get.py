import requests
import logging


from infra.http.retry import RetryPolicy

retry_policy = RetryPolicy()
logger = logging.getLogger('lucroadmin.adapters.mercadolivre')


class RequestMercadoPago:
    def request_endpoint_mercadopago(self, url: str, headers: dict[str, str]):

        logger.info(
            'Mercado Pago Request | Enviando requisição para o end point %s',
            url,
        )
        response = requests.get(url=url, headers=headers, timeout=20)
        return response


class GetMercadoPago:
    def get_endpoints_mercadopago(self, access_token: str, url: str):
        """
        :param self: Objeto
        :param access_token: Credencial de acesso válida
        :type access_token: string
        :param url: Endpoint Mercado Livre
        :type url: String

        Headers e request para endpoint Mercado Livre para retornar ao service o json.
        """
        logger.info(
            'Mercado Pago get_endpoints_mercadopago | Iniciando o Request'
        )
        headers: dict[str, str] = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }

        request = RequestMercadoPago()
        response = retry_policy.executa(
            lambda: request.request_endpoint_mercadopago(url, headers)
        )
        logger.info(
            'Bling get_endpoints_bling | Retorno da requisição é %s',
            response.status_code,
        )

        return response
