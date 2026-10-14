import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from lucro_admin.adapters.bling.bling_orders import CrudBling
from lucro_admin.core.entities import PageOrders
from lucro_admin.core.entities_pedidos import (
    ItemList,
    OrderByPage,
    OrderDetail,
    OrderItemInsert,
)
from lucro_admin.infra.repository.repository_marketplaces import Marketplaces
from lucro_admin.infra.repository.repository_order_item import OrderItem
from lucro_admin.infra.repository.repository_order_page import OrderPage
from lucro_admin.infra.repository.repository_orders import Orders
from lucro_admin.infra.repository.repository_pipeline_execution import (
    PipelineExecution,
)
from lucro_admin.infra.repository.repository_products import Products
from lucro_admin.services.bling.credentials.providers.bling_provider import (
    BlingProvider,
)
from lucro_admin.services.bling.orders.order_situation_bling import (
    OrderSituationBling,
)
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)
from lucro_admin.services.token_service import TokenService

logger = logging.getLogger('lucroadmin.services.blingpedidos')


async def order_items(self, items, session):
    repository = OrderItem(session)
    product_repo = Products(session)
    order_items_insert = []
    for item_list in items:
        for item in item_list.items:
            product = await product_repo.consult_product_with_sku(
                sku=item['codigo']
            )
            if product == []:
                product = await product_repo.consult_product_with_full_sku(
                    full_sku=item['codigo']
                )
            order_items_insert.append(
                OrderItemInsert(
                    order_id=item_list.order_id,
                    situation_id=item_list.situation_id,
                    product_id=product[0][0],
                    quantity=item['quantidade'],
                    cost_price=product[0][2],
                    unit_selling_price=item['valor']
                )
            )
    logger.info(
        'Bling Orders Order Item | '
        'Order Items added %s',
        len(order_items_insert),
    )
    await repository.insert_ordem_item(order_items_insert)


async def data_modeling_order(order, situation_id, session):
    repo_mkt = Marketplaces(session=session)
    if order['loja']['id'] == 0:
        marketplace_id = await repo_mkt.select_marketplace(
        1
        )
    else:
        marketplace_id = await repo_mkt.select_marketplace(
            order['loja']['id']
        )
    return OrderByPage(
        external_id=order['id'],
        origin_id=order['numero'],
        situation_id=situation_id,
        marketplace_id=marketplace_id[0][0],
        marketplace_order_id=order['numeroLoja'],
        order_date=order['data']
        )


class Attended:
    """
    Attended -> Getting orders in the served status

    """

    def __init__(self):
        self.provider = BlingProvider()
        self.token_service = TokenService(self.provider)
        self.access_token = self.token_service.validate_access_token()
        self.adapt_pedidos = CrudBling()
        self.service_base = BaseRequestHTTP(
            self.adapt_pedidos, self.access_token
        )
        self.base_url = 'https://api.bling.com.br/Api/v3'
        self.order_situation = OrderSituationBling(
            adapt_order=self.adapt_pedidos,
            access_token=self.access_token
        )

    def url_endpoint_pag(
        self,
        page: int,
        situation: int,
        initical_date: datetime,
        final_date: datetime
    ) -> str:
        """
        url_endpoint_pag -> URL Assembly

        :param self: Object
        :param pagina: Page for endpoint
        :type pagina: int
        :param sit: Bling situation number
        :type sit: int
        :param data_inicial: Orders that were placed from this date
        :type data_inicial: date
        :param data_final: Orders placed until this date
        :type data_final: date
        :return: Properly assembled endpoint
        :rtype: str
        """
        url: str = (
            f'{self.base_url}/pedidos/vendas?pagina={page}&limite=100&'
            f'idsSituacoes%5B%5D={situation}&dataAlteracaoInicial={initical_date}'
            f'&dataAlteracaoFinal={final_date}'
        )
        return url

    async def get_id_by_page(self, session):
        """
        get_id_por_pag -> Orquestrando as requisições para obter ids das vendas

        :param self: Objeto
        :return: Ids das vendas
        :rtype: ResultadoGetPaginas
        """
        sit = await self.order_situation.situation_data_base('Atendido')
        more_page: bool = True
        repository = Orders(session=session)
        repository_page = OrderPage(session=session)
        repository_pipeline = PipelineExecution(session=session)

        order_page = await repository_page.select_pending_order_page(
            situation_id=sit.situation_bling_id,
            integration_id=1
        )
        end_date = datetime.now(ZoneInfo('America/Sao_Paulo'))
        orders = []
        page = 1
        while more_page:
            url = self.url_endpoint_pag(
                page=page,
                situation=sit.situation_bling_id,
                initical_date=order_page.date_page,
                final_date=end_date
            )
            logger.info(
                'Bling Orders get_id_por_pag | '
                'Endpoint URL %s', url
            )
            response = self.service_base.organiza_get_request(url)

            if response.status == 'ok':
                data = response.data.get('data', [])
                for sale in data:
                    orders.append(
                        await data_modeling_order(
                            order=sale,
                            situation_id=sit.situation_id,
                            session=session
                        )
                    )

                if len(data) < 100:
                    more_page = False
                    order_page_insert = PageOrders(
                                id=None,
                                date_page=end_date,
                                page=page,
                                more_orders=False,
                                situation_id=sit.situation_bling_id,
                                integration_id=1
                            )
                else:
                    page += 1

            else:
                logger.critical(
                    'Bling Pedidos get_id_por_pag | Request Error %s -> ',
                    response.error,
                )
                return

        insert_orders = await repository.insert_order(orders=orders)

        await repository_page.insert_order_page(
            orders_page=order_page_insert
        )

        if len(insert_orders) > 0:
            await repository_pipeline.insert_pipeline_execution(
                orders_id=[order[0] for order in insert_orders],
                stage_id=1,
                status_id=2
            )

        await session.commit()


class OrderDetails:
    """
    OrderDetails ->
    You process the provided IDs to obtain further details about the sale.

    """

    def __init__(self):
        self.provider = BlingProvider()
        self.token_service = TokenService(self.provider)
        self.access_token = self.token_service.validate_access_token()
        self.adapt_pedidos = CrudBling()
        self.service_base = BaseRequestHTTP(
            self.adapt_pedidos, self.access_token
        )
        self.order_situation = OrderSituationBling(
            adapt_order=self.adapt_pedidos,
            access_token=self.access_token
                )
        self.base_url = 'https://api.bling.com.br/Api/v3'

    def url_id(self, id) -> str:
        """
        url_id -> Montage da URL endpoint

        :param self: Objeto
        :param id: Id único por venda gerado pelo Bling
        :return: URL endpoint com id
        :rtype: str
        """
        return f'{self.base_url}/pedidos/vendas/{id}'

    async def get_id_details(self, session):
        orders_detail = []
        items = []
        situation = await self.order_situation.situation_data_base('Atendido')
        repository = Orders(session=session)
        repository_pipeline = PipelineExecution(session=session)
        more_page: bool = True
        offset = 0
        pipeline_update = []
        while more_page:
            pipelines = await repository_pipeline.select_pipeline_execution(
                stage_id=1,
                status_id=2,
                offset=offset
            )
            for pipeline in pipelines:
                order_data = await repository.select_order_id(
                    order_id=pipeline[1]
                )
                url = self.url_id(order_data[1])
                logger.info(
                'Bling Orders get_id_details | '
                'Url montada %s', url
            )
                response = self.service_base.organiza_get_request(url)
                if response.status == 'ok':
                    data = response.data.get('data', [])
                    transporte = data.get('transporte') or {}
                    volumes = transporte.get('volumes') or []

                    orders_detail.append(
                        OrderDetail(
                            order_id=pipeline[1],
                            external_invoice_id=data['notaFiscal']['id'],
                            value_order=data['total'],
                            uf_dest=data['transporte']['etiqueta']['uf'],
                            transport=volumes[0].get('servico')
                            if volumes
                            else 'SEM_SERVIÇO',
                        )
                    )
                    items.append(
                        ItemList(
                            order_id=pipeline[1],
                            situation_id=situation.situation_id,
                            items=data['itens'],
                        )
                    )

                    pipeline_update.append(
                        {
                            'pipeline_id': pipeline[0],
                            'order_id': pipeline[1],
                            'status_id': 1
                        }
                    )

                    logger.info(
                        'Bling Service Order Details | '
                        'Endpoint %s / Response %s',
                        url,
                        response.data,
                    )
                else:
                    logger.error(
                        'Bling Order Detail | '
                        'Request Error %s',
                        response.error,
                    )

            if len(pipelines) < 100:
                more_page = False
            else:
                offset += 100

        await repository.update_order_details(orders_detail)

        await order_items(items=items, session=session)

        await repository_pipeline.insert_pipeline_execution(
            [(order['order_id']) for order in pipeline_update],
            2,
            2
        )

        await repository_pipeline.update_pipeline_execution(pipeline_update)

        await session.commit()
