import logging
from datetime import datetime

from lucro_admin.core.entities_pedidos import ErrorHTTP, PageResult
from lucro_admin.core.entities_produtos import Product
from lucro_admin.infra.repositorio_produtos import Produtos
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.blingproducts')


class ProductsRequestBling:
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
        self.repository = Produtos()
        self.url_base = 'https://api.bling.com.br/Api/v3'

    def url_products_endpoint_pag(self, page: int) -> str:
        """
        :param pag: Pagina da listagem de produtos
        :type pag: int

        :return: Url de endpoint correta
        :rtype: str
        """
        url: str = (
            f'{self.url_base}/produtos?pagina={page}&limite=100'
        )

        return url

    def get_produtos_pag(self):

        products_db = self.repository.consulta_todos_produtos()
        page: int = 1
        more_page: bool = True
        page_limit_return: int = 100
        new_products: list[int] = []
        error429: list[ErrorHTTP] = []

        logger.info(
            'Bling Product get_products_pag |'
            ' Starting a requests to serching new products'
        )
        while more_page:
            url: str = self.url_products_endpoint_pag(page=page)
            logger.info(
                'Bling Product get_products_pag |'
                ' Sending request to endpoint %s',
                url
            )
            response: PageResult = self.service_base.organiza_get_request(
                url=url
            )

            if response.status == 'ok':
                data: dict = response.data.get('data', [])
                id_page: list[int] = [product['id'] for product in data]
                for id in id_page:
                    if id not in products_db:
                        new_products.append(id)

                if len(id_page) < page_limit_return:
                    more_page = False
                else:
                    page += 1

            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Products get_products_pag | Request Error %s',
                    response.error,
                )
                error: ErrorHTTP = ErrorHTTP(
                        status=response.error['status'],
                        error=response.error['body'],
                        method='get_id_por_pag',
                        class_name='Atendidos',
                        module='service_bling_pedidos.py',
                        endpoint=url,
                        data=datetime.now(),
                        )
                error429.append(error)
                page += 1
            else:
                logger.critical(
                    'Bling Products get_products_pag | error request %s',
                    response.error,
                )
                raise Exception(
                    f'Request Error: {response.status} - {response.error}'
                )
        new_products_qnt: int = len(new_products)
        if new_products_qnt > 0:
            logger.info(
                'Bling Products get_products_pag | '
                'Found %s new products',
                new_products_qnt
                )
            products_detail = self.get_details_product(new_products)
            logger.info(
                'Bling Products get_products_pag |'
                'Newly registered products \n %s',
                products_detail
            )
        else:
            return 'Not founded new products'

    def get_details_product(self, ids_list):

        logger.info(
            'Bling Produtts get_details_item | '
            'Starting get details '
        )
        new_products: list[Product] = []
        for id in ids_list:
            url: str = f'{self.url_base}/produtos/{id}'
            logger.info(
                'Bling Produtts get_details_item | '
                'Sending request ot endpoint %s',
                url
            )

            response: PageResult = self.service_base.organiza_get_request(url)

            if response.status == 'ok':
                data = response.data.get('data', [])
                product: Product = Product(
                    product_bling_id=data['id'],
                    sku=data['codigo'],
                    product_description=data['nome'],
                    supplier=data['fornecedor']['contato']['nome'],
                    cost_price=data['fornecedor']['precoCusto'],
                    origin=data['tributacao']['origem'],
                    ncm=data['tributacao']['ncm'],
                    cest=data['tributacao']['cest']
                )

                new_products.append(product)

            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Product get_details_product | '
                    'Rated Limit response return %s',
                    response.error,
                )
                continue

            else:
                logger.critical(
                    'Bling Products get_details_product | '
                    'Critical Error response request %s',
                    response.error,
                )
                raise Exception(
                    f'Critical Error: {response.status} - {response.error}'
                )

        return new_products
