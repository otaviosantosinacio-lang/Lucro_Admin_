import logging
from datetime import date, datetime

from lucro_admin.core.entities_pedidos import (
    ErrorHTTP,
    OrderData,
    OrderDetail,
    OrderPage,
)
from lucro_admin.core.marketplace import nome_marketplace
from lucro_admin.infra.database_.session import SessionLocal
from lucro_admin.infra.repository_marketplaces import Marketplaces
from lucro_admin.infra.repository_orders import Orders
from lucro_admin.services.bling.orders.order_situation_bling import (
    OrderSituationBling,
)
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)

logger = logging.getLogger('lucroadmin.services.blingpedidos')


class Attended:
    """
    Attended -> Getting orders in the served status

    """

    def __init__(self, access_token, adapt_pedidos):
        self.access_token = access_token
        self.adapt_pedidos = adapt_pedidos
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
            f'idsSituacoes%5B%5D={sit}&dataInicial=2026-07-01'
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
            repository_mkt = Marketplaces(session=session)
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
                            marketplace_id = await repository_mkt.get_marketplace(
                            1
                            )
                        else:
                            marketplace_id = await repository_mkt.get_marketplace(
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
            await session.close()


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

    async def get_id_details(self) -> OrderDetail:
        """
        get_id_detalhes

        :param self: Objeto
        :param ids_list: Lista de ids da situação selecionada
        :type ids_list: list[int]
        """
        error429 = []
        pedidos = []
        sit = await self.order_situation.situation_data_base('Atendido')
        async with SessionLocal() as session:
            repository = Orders(session=session)

            more_page: bool = False
            offset = 0
            while more_page:
                ids = await repository.orders_without_details(
                    offset=offset,
                    situation_id=sit.situation_id
                )
                for id in ids:
                    url = self.url_id(id[1])
                    response = self.service_base.organiza_get_request(url)

                    if response.status == 'ok':
                        data = response.data.get('data', [])
                        id_loja = data['loja']['id']
                        nome_mkt = nome_marketplace(id_loja)
                        transporte = data.get('transporte') or {}
                        volumes = transporte.get('volumes') or []

                        pedido: OrderDetail = OrderDetail(
                            nf_id=data['notaFiscal']['id'],
                            value_sale=data['total'],
                            items=data['itens'],
                            uf_dest=data['transporte']['etiqueta']['uf'],
                            servico_trans=volumes[0].get('servico')
                            if volumes
                            else 'SEM_SERVIÇO',
                        )
                        logger.info(
                            'Bling Service get_id_detalhes | '
                            'Dados do pedido %s',
                            pedido,
                        )
                        pedidos.append(pedido)

                        logger.info(
                            'Bling Service get_id_detalhes | '
                            'Endpoint %s / Retorno %s',
                            url,
                            response.data,
                        )
                    elif response.status == 'rated_limit':
                        logger.error(
                            'Bling Pedidos get_id_detalhes | '
                            'Erro na requisição %s',
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
                    return
