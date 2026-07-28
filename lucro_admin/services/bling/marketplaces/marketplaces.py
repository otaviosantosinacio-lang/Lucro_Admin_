import logging

from lucro_admin.core.entities_pedidos import PageResult
from lucro_admin.core.marketplace import Marketplace
from lucro_admin.services.service_http_request_base import BaseRequestHTTP

logger = logging.getLogger('lucroadmin.services.blingmarketplaces')


class MarketplaceBling:

    def __init__(
        self,
        access_token,
        adapter
    ):
        self.access_token = access_token
        self.adapter = adapter
        self.base_request = BaseRequestHTTP(
            adapter,
            access_token
        )
        self.base_url = 'https://api.bling.com.br/Api/v3'

    def get_marketplaces(self):

        breakpoint()
        page: int = 1
        more_page: bool = True
        marketplaces = []
        while more_page:
            url: str = f'{self.base_url}/canais-venda?pagina{page}=&limite=100'
            logger.info(
                'Bling Marketplaces |'
                'Send request get marketplaces to endpoint %s',
                url
            )

            response: PageResult = self.base_request.organiza_get_request(
                url
            )
            if response.status == 'ok':
                data = response.data.get('data', [])
                logger.info(
                    'Bling Marketplaces |'
                    'Returned marketplaces %s',
                    data
                )
                for mkt in data:
                    marketplaces.append(
                        Marketplace(
                            external_id=mkt['id'],
                            external_type=mkt['tipo'],
                            marketplace_name=mkt['descricao']
                        )
                    )
                breakpoint()
                if len(data) < 100:
                    more_page = False

            elif response.status == 'rated_limit':
                logger.warning(
                    'Bling Marketplaces | '
                    'The request marketplaces return %s status code',
                    response.status
                )
                continue

            else:
                logger.critical(
                    'Bling Marketplaces | '
                    'Response request returning critical status ->'
                    f'{response.status}',
                )
                return None

        logger.info(
                    'Bling Marketplaces |'
                    'Returned marketplaces %s',
                    marketplaces
                )
