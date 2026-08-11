import logging
from datetime import datetime

from lucro_admin.core.entities_pedidos import ErrorHTTP, PageResult
from lucro_admin.core.entities_logistics import RegisterLogistic
from lucro_admin.infra.database_.session import SessionLocal
from lucro_admin.infra.repository_products import Products
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.bling.logistics')


class Logistics():

    def __init__(
        self,
        access_token,
        adapt_bling,
    ):
        self.access_token = access_token
        self.adapt_pedidos = adapt_bling
        self.service_base = BaseRequestHTTP(
            adapt_pedidos=self.adapt_pedidos, access_token=self.access_token
        )
        self.url_base = 'https://api.bling.com.br/Api/v3'

    def build_url_page(self, page):

        url: str = f'{self.url_base}/logisticas?pagina={page}&limite=100'

        return url

    def logistic_page(self):

        more_page: bool = True
        page = 1
        logistics_id = []
        error429 = []
        while more_page:
            logger.info(
                'Bling Logistics Page | '
                'Starting get logistics id'
            )
            url: str = self.build_url_page(page=page)

            response = self.service_base.organiza_get_request(url)

            if response.status == 'ok':
                print(response.data)
                data = response.data.get('data', [])
                for id in data:
                    logistics_id.append(id['id'])

                if len(data) < 100:
                    more_page: bool = False
                else:
                    page += 1

            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Logistics| Request Error %s',
                    response.error,
                )
                error: ErrorHTTP = ErrorHTTP(
                        status=response.error['status'],
                        error=response.error['body'],
                        method='logistic_page',
                        class_name='Logistics',
                        module='logistics_bling.py',
                        endpoint=url,
                        data=datetime.now(),
                        )
                error429.append(error)
                page += 1
            else:
                logger.critical(
                    'Bling Logistics | error request %s',
                    response.error,
                )
                raise Exception(
                    f'Request Error: {response.status} - {response.error}'
                )

        logistics_detail = self.logistic_services(logistics_id)

    def logistic_services(self, logistics_id):

        logger.info(
                'Bling Logistics Services | '
                'Starting get services logistics'
            )
        error429 = []
        logistics_services = []

        for id in logistics_id:
            url = (
                f'{self.url_base}/logisticas/{id}?listarServicosInativos=true'
            )

            response = self.service_base.organiza_get_request(url)

            if response.status == 'ok':
                breakpoint()
                print(response.data)
                data = response.data.get('data', [])
                logistic_name: str = data['tipoIntegracao']
                for service in data['servicos']:
                    logistics_services.append(
                        RegisterLogistic(
                            external_service_id=service['id'],
                            service_name=service['descricao'],
                            logistics_name=logistic_name,
                            status=service['ativo'],
                        )
                    )
            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Logistics| Request Error %s',
                    response.error,
                )
                error: ErrorHTTP = ErrorHTTP(
                        status=response.error['status'],
                        error=response.error['body'],
                        method='logistic_services',
                        class_name='Logistics',
                        module='logistics_bling.py',
                        endpoint=url,
                        data=datetime.now(),
                        )
                error429.append(error)
            else:
                logger.critical(
                    'Bling Logistics | error request %s',
                    response.error,
                )
                raise Exception(
                    f'Request Error: {response.status} - {response.error}'
                )