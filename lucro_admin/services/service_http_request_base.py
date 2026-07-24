import logging
from http import HTTPStatus

from lucro_admin.core.entities_pedidos import PageResult

logger = logging.getLogger('lucroadmin.services.baserequesthttp')


class BaseRequestHTTP:
    def __init__(self, adapt_pedidos, access_token: str):
        self.adapt_pedidos = adapt_pedidos
        self.access_token = access_token

    def organiza_get_request(self, url: str) -> PageResult:
        """

        url: str

        Padroniza retorno de Api externa.

        """
        response = self.adapt_pedidos.get_endpoint(
            self.access_token, url
        )

        if response.status_code == HTTPStatus.OK:
            data = response.json()
            logger.info(
                'BaseRequestHTTP organiza_get_request | Retorno da endpoint %s',
                response.status_code,
            )
            return PageResult(status='ok', data=data)

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            logger.error(
                'BaseRequestHTTP organiza_get_request |'
                ' Retorno da endpoint %s -> %s ',
                response.status_code,
                response.text,
            )
            return PageResult(
                status='rated_limit',
                error={'url': url, 'status': 429, 'body': response.text},
            )
        logger.critical(
            'BaseRequestHTTP organiza_get_request |'
            ' Retorno da endpoint %s -> %s ',
            response.status_code,
            response.text,
        )
        return PageResult(
            status='error',
            error={'status': response.status_code, 'body': response.text},
        )
