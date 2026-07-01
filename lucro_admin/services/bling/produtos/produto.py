import logging

from lucro_admin.services.bling.pedidos.service_bling_base_pedidos import (
    BaseHTTPBling
)
from lucro_admin.core.entities_produtos import Produto
from lucro_admin.infra.repositorio_produtos import Produtos

logger = logging.getLogger('lucroadmin.services.blingprodutos')


class ProdutosRequest:

    def __init__(self, access_token, adapt_bling, ):
        self.access_token = access_token
        self.adapt_pedidos = adapt_bling
        self.service_base = BaseHTTPBling(
            adapt_pedidos=self.adapt_pedidos, access_token=self.access_token
        )

    def url_produtos_endpoint(self, pag: int) -> str:

        '''
        :param pag: Pagina da listagem de produtos
        :type pag: int

        :return: Url de endpoint correta
        :rtype: str
        '''
        url: str = f'https://api.bling.com.br/Api/v3/produtos?pagina={pag}&limite=100'

        return url



'''    
def get_produtos_pag(self):

        produtos_db= Produtos.
        while
        
'''