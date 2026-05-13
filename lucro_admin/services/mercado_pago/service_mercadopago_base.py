import logging

from lucro_admin.core.entities_pedidos import ResultadoPagina

logger = logging.getLogger('lucroadmin.services.mercadolivre')


class BaseHTTPMercadoPago:
    def __init__(self, adapt_pedidos, access_token: str):
        self.adapt_pedidos = adapt_pedidos
        self.access_token = access_token

    def organiza_get_request(self, url: str) -> ResultadoPagina:
        """

        url: str

        Chama api MercadoLivre mediante a endpoint (url) e padroniza o retorno.

        """
        response = self.adapt_pedidos.get_endpoints_mercadopago(
            self.access_token, url
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(
                'Mercado pago organiza_get_request | Retorno da endpoint %s',
                response.status_code,
            )
            return ResultadoPagina(status='ok', data=data)

        if response.status_code == 429:
            logger.error(
                'Mercado Livre organiza_get_request | Retorno da endpoint %s -> %s ',
                response.status_code,
                response.text,
            )
            return ResultadoPagina(
                status='rated_limit',
                error={'url': url, 'status': 429, 'body': response.text},
            )
        logger.critical(
            'Mercado Livre organiza_get_request | Retorno da endpoint %s -> %s ',
            response.status_code,
            response.text,
        )
        return ResultadoPagina(
            status='error',
            error={'status': response.status_code, 'body': response.text},
        )
