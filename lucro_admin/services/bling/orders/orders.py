import logging
from datetime import date, datetime

from lucro_admin.adapters.bling.bling_orders import CrudBling
from lucro_admin.core.entities_pedidos import (
    ErrorHTTP,
    ItemList,
    OrderDetail,
    OrderItemInsert,
    OrderPage,
)
from lucro_admin.infra.database import SessionLocal
from lucro_admin.infra.repository_marketplaces import Marketplaces
from lucro_admin.infra.repository_order_item import OrderItem
from lucro_admin.infra.repository_orders import Orders
from lucro_admin.infra.repository_products import Products
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
        self, pagina: int, sit: int, data_inicial: date, data_final: date
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
            f'{self.base_url}/pedidos/vendas?pagina={pagina}&limite=100&'
            f'idsSituacoes%5B%5D={sit}&dataInicial={data_inicial}'
            f'&dataFinal={data_final}'
        )
        return url

    async def get_id_by_page(self):
        """
        get_id_por_pag -> Orquestrando as requisições para obter ids das vendas

        :param self: Objeto
        :return: Ids das vendas
        :rtype: ResultadoGetPaginas
        """
        limit_orders: int = 100
        sit = await self.order_situation.situation_data_base('Atendido')
        more_page: bool = True
        page = 1
        async with SessionLocal() as session:
            repository = Orders(session=session)
            repo_mkt = Marketplaces(session=session)
            repo_initial_date = await repository.last_date_order()

            initial_date = repo_initial_date[0][0]
            if initial_date is None:
                initial_date = datetime.now().date()

            end_date = datetime.now().date()
            orders = []
            error429 = []

            while more_page:
                url = self.url_endpoint_pag(
                    page, sit.situation_bling_id, initial_date, end_date
                )
                logger.info(
                    'Bling Orders get_id_por_pag | '
                    'Url montada %s', url
                )
                response = self.service_base.organiza_get_request(url)

                if response.status == 'ok':
                    data = response.data.get('data', [])
                    for sale in data:
                        if sale['loja']['id'] == 0:
                            marketplace_id = await repo_mkt.get_marketplace(
                            1
                            )
                        else:
                            marketplace_id = await repo_mkt.get_marketplace(
                                sale['loja']['id']
                            )
                        order: OrderPage = OrderPage(
                            external_id=sale['id'],
                            origin_id=sale['numero'],
                            situation_id=sit.situation_id,
                            marketplace_id=marketplace_id[0][0],
                            marketplace_order_id=sale['numeroLoja'],
                            order_date=sale['data']
                        )
                        logger.info(
                        'Bling Orders get_id_por_pag | '
                        'Order %s',
                    )

                        orders.append(order)

                    if len(data) < limit_orders:
                        more_page = False
                    else:
                        page += 1

                elif response.status == 'rated_limit':
                    logger.error(
                        'Bling Pedidos get_id_por_pag | Erro na requisição %s',
                        response.error,
                    )
                    erro = ErrorHTTP(
                        status=response.error['status'],
                        error=response.error['body'],
                        method='get_id_by_pag',
                        class_name='Attended',
                        module='service_bling_orders.py',
                        endpoint=url,
                        data=datetime.now(),
                    )
                    error429.append(erro)
                    page += 1

                else:
                    logger.critical(
                        'Bling Pedidos get_id_por_pag | Erro na requisição %s',
                        response.error,
                    )
                    raise Exception(
                    f'Erro na requisição: {response.status} - {response.error}'
                    )

            await repository.insert_order(orders=orders)

            await session.commit()


class OrderDetails:
    """
    OrderDetails ->
    You process the provided IDs to obtain further details about the sale.

    """

    def __init__(self, access_token, adapt_pedidos):
        self.access_token = access_token
        self.adapt_pedidos = adapt_pedidos
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

    async def get_id_details(self):
        """
        get_id_detalhes

        :param self: Objeto
        :param ids_list: Lista de ids da situação selecionada
        :type ids_list: list[int]
        """
        error429 = []
        orders_detail = []
        items = []
        sit = await self.order_situation.situation_data_base('Atendido')
        async with SessionLocal() as session:
            repository = Orders(session=session)
            more_page: bool = True
            offset = 0
            while more_page:
                ids = await repository.orders_without_details(
                    offset=offset,
                    situation_id=sit.situation_id
                )
                for id in ids:
                    url = self.url_id(id[1])
                    logger.info(
                    'Bling Orders get_id_details | '
                    'Url montada %s', url
                )
                    response = self.service_base.organiza_get_request(url)
                    if response.status == 'ok':
                        data = response.data.get('data', [])
                        transporte = data.get('transporte') or {}
                        volumes = transporte.get('volumes') or []

                        order: OrderDetail = OrderDetail(
                            order_id=id[0],
                            external_invoice_id=data['notaFiscal']['id'],
                            value_order=data['total'],
                            uf_dest=data['transporte']['etiqueta']['uf'],
                            transport=volumes[0].get('servico')
                            if volumes
                            else 'SEM_SERVIÇO',
                        )
                        items.append(
                            ItemList(
                                order_id=id[0],
                                situation_id=sit.situation_id,
                                items=data['itens'],
                            )
                        )
                        logger.info(
                            'Bling Service Order Details | '
                            'Order data %s',
                            order,
                        )
                        orders_detail.append(order)

                        logger.info(
                            'Bling Service Order Details | '
                            'Endpoint %s / Response %s',
                            url,
                            response.data,
                        )
                    elif response.status == 'rated_limit':
                        logger.error(
                            'Bling Pedidos Order Detail | '
                            'Request Error %s',
                            response.error,
                        )
                        erro = ErrorHTTP(
                            status=response.error['status'],
                            error=response.error['body'],
                            method='get_id_detalhes',
                            class_name='ProcessaId',
                            module='service_bling_pedidos.py',
                            endpoint=url,
                            data=datetime.now(),
                        )
                        error429.append(erro)
                if len(ids) < 100:
                    more_page = False
                else:
                    offset += 100

            await repository.insert_order_details(orders_detail)

            await self.order_items(items=items, session=session)

            await session.commit()

            await session.close()

            return

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
