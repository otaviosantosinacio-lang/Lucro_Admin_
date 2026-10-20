import logging
from collections import defaultdict
from typing import Any

from lucro_admin.adapters.mercado_livre.mercado_livre_orders import (
    GetMercadoLivre,
)
from lucro_admin.core.entities_pedidos import (
    IdsPedidoML,
    ItemComissionShip,
    PageResult,
    SaleCosts,
)
from lucro_admin.core.order_item import OrderItemDB
from lucro_admin.core.pipelines import PipelinesExecution
from lucro_admin.infra.repository.repository_order_item import OrderItem
from lucro_admin.infra.repository.repository_pipeline_execution import (
    PipelineExecution,
)
from lucro_admin.services.mercado_livre.tokens.ml_provider import MLProvider
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)
from lucro_admin.services.token_service import TokenService

logger = logging.getLogger('lucroadmin.services.mercadolivrepedidos')


def endpoint_order(id_venda: int) -> str:

    url = f'https://api.mercadolibre.com/orders/{id_venda}'
    return url


def endpoint_pack(id_pack: int) -> str:

    url = f'https://api.mercadolibre.com/packs/{id_pack}'
    return url


def union_order_items(order_items):
    temp_grouping = defaultdict(list)

    for item in order_items:
        temp_grouping[item.order_id].append(item)

    list_order_items = list(temp_grouping.values())

    return list_order_items


class MeliCosts:

    def __init__(self):
        self.provider = MLProvider()
        self.token_service = TokenService(self.provider)
        self.access_token = self.token_service.validate_access_token()
        self.adapter = GetMercadoLivre()
        self.service_base = BaseRequestHTTP(
            self.adapter, self.access_token
        )

    def extract_packid_payid(self, url: str) -> IdsPedidoML:

        response: PageResult = self.service_base.organiza_get_request(
            url=url
        )

        if response.status == 'ok':
            return IdsPedidoML(
                comissao=response.data['order_items'][0]['sale_fee'],
                pay_id=response.data['payments'][0]['id'],
                pack_id=response.data['pack_id'],
                geral=response.data,
                status=response.status
            )

        else:
            return IdsPedidoML(
                comissao=0.0,
                pay_id=0,
                pack_id=0,
                geral=response.data,
                status=response.status
            )

    async def get_sale_costs(self, session):

        logger.info(
        'Mercado Livre Costs | '
        'Starting the extraction of necessary IDs from the Order.'
        )
        repository = OrderItem(session=session)
        repository_pipeline = PipelineExecution(session=session)
        offset: int = 0
        more_page: bool = True
        item_costs = []
        while more_page:
            pipelines_id: list[PipelinesExecution] = (
                await repository_pipeline.select_pipeline_execution(
                stage_id=4,
                status_id=2,
                integration_id=2,
                offset=offset
                )
            )

            order_items_pipeline: list[OrderItemDB] = (
                await repository.select_order_item(
                pipelines=pipelines_id
                )
            )

            orders_items = union_order_items(
                order_items=order_items_pipeline
            )
            for order_items in orders_items:
                costs = self.get_commision_ship_cost(
                    meli_order=order_items[0].marketplace_order_id,
                    order_items=order_items
                )
                if costs is None:
                    continue
                for item in costs:
                    if order_items == 'Mercado Envios Flex':
                        shipping: float = 12.99
                        item.item_shipping = shipping
                        item_costs.append(item)
                    else:
                        item_costs.append(item)

            if len(order_items_pipeline) < 100:
                more_page = False
            else:
                offset += 100

        await repository.update_shipping_commission(item_costs)

        await session.commit()

    def get_commision_ship_cost(
        self,
        meli_order,
        order_items
        ):

        url: str = endpoint_order(id_venda=meli_order)

        logger.info('Mercado Livre Costs | EndPoint order %s', url)

        response: IdsPedidoML = self.extract_packid_payid(url=url)

        logger.info('Mercado Livre Costs | Return -> %s', response)
        commission_ship_cost: SaleCosts | Any = []
        if response.status != 'ok':
            return None

        if response.pack_id is not None:
            ids = self.get_ids_pack(id_pack=response.pack_id)

            if ids['status'] == 'ok':
                for id in ids['ids']:
                    id_order = id['id']
                    url: str = endpoint_order(id_venda=id_order)

                    response_melisale: PageResult = (
                        self.service_base.organiza_get_request(url=url)
                    )

                    commission = response_melisale.data['order_items'][0][
                        'sale_fee'
                    ]

                    ship_cost = self.get_ship_cost(
                        response_melisale.data['shipping']['id']
                    )

                    for item in order_items:
                        if item.sku == response_melisale.data[
                            'order_items'][
                                0][
                                    'item'][
                                        'seller_sku']:
                            commission_ship_cost.append(
                                ItemComissionShip(
                                order_item_id=item.order_item_id,
                                item_shipping=ship_cost,
                                item_commission=commission,
                                )
                            )
                        else:
                            continue
        else:
            commission = response.comissao
            ship_cost: float = self.get_ship_cost(
                        response.geral['shipping']['id']
                        )
            commission_ship_cost.append(
                ItemComissionShip(
                    order_item_id=order_items[0].order_item_id,
                    item_shipping=ship_cost,
                    item_commission=commission,
                )
            )
        return commission_ship_cost

    def get_ship_cost(self, ship_id):

        url: str = f'https://api.mercadolibre.com/shipments/{ship_id}/costs'
        response = self.service_base.organiza_get_request(url=url)
        custo_frete = response.data['senders'][0]['cost']
        return custo_frete

    def get_ids_pack(self, id_pack):

        url = endpoint_pack(id_pack=id_pack)

        response = self.service_base.organiza_get_request(url=url)

        if response.status == 'ok':
            ids_venda = response.data['orders']
            return {'status': 'ok', 'ids': ids_venda}
