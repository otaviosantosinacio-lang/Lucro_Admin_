import logging
from datetime import datetime

from lucro_admin.core.entities_pedidos import ErrorHTTP
from lucro_admin.core.entities_produtos import Produto
from lucro_admin.infra.repositorio_produtos import Produtos
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.blingproducts')


class ProdutosRequest:
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

    def url_products_endpoint_pag(self, page: int) -> str:
        """
        :param pag: Pagina da listagem de produtos
        :type pag: int

        :return: Url de endpoint correta
        :rtype: str
        """
        url: str = (
            f'https://api.bling.com.br/Api/v3/produtos?pagina={page}&limite=100'
        )

        return url

    def get_produtos_pag(self):

        products_db = self.repository.consulta_todos_produtos()
        page: int = 1
        more_page: bool = True
        page_limit_return: int = 100
        new_products: list[int] = []
        error429 = []
        while more_page:
            url = self.url_products_endpoint_pag(page=page)
            response = self.service_base.organiza_get_request(url=url)

            if response.status == 'ok':
                data = response.data.get('data', [])
                id_page: list[int] = [product['id'] for product in data]
                for id in id_page:
                    if not id in products_db:
                        new_products.append(id)

                if len(id_page) < page_limit_return:
                    more_page = False
                else:
                    page += 1

            elif response.status == 'rated_limit':
                logger.error(
                    'Bling Produtcts get_products_pag | Request Error %s',
                    response.error,
                )
                error = ErrorHTTP(
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
                    'Bling Produtcts get_products_pag | error request %s',
                    response.error,
                )
                raise Exception(
                    f'Request Error: {response.status} - {response.error}'
                )

        if len(new_products) > 0:
            self.get_details_item(new_products)
        else:
            return 'Nenhum prodto para ser inserido'
    def get_details_item(self, ids_list):
        ...