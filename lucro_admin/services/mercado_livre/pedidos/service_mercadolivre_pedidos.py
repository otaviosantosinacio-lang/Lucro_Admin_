import logging
from typing import Any

from lucro_admin.core.entities_pedidos import (
    IdsPedidoML,
    ItemComissionShip,
    PageResult,
    SaleCosts,
)
from lucro_admin.infra.database_.session import SessionLocal
from lucro_admin.infra.repository_order_item import OrderItem
from lucro_admin.services.mercado_pago.service_mercadopago import (
    MercadoPagoCustos,
)
from lucro_admin.services.service_http_request_base import (
    BaseRequestHTTP,
)

logger = logging.getLogger('lucroadmin.services.mercadolivrepedidos')


def endpoint_order(id_venda: int) -> str:

    url = f'https://api.mercadolibre.com/orders/{id_venda}'
    return url


def endpoint_pack(id_pack: int) -> str:

    url = f'https://api.mercadolibre.com/packs/{id_pack}'
    return url


class ExtraiCustoMercadoLivre:

    def __init__(self, access_token, adapt_pedido):
        self.access_token = access_token
        self.adapt_pedido = adapt_pedido
        self.service_base = BaseRequestHTTP(
            self.adapt_pedido, self.access_token
        )
        self.mercado_pago = MercadoPagoCustos()

    def extraindo_packid_payid(self, url: str) -> IdsPedidoML:

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

    async def get_sale_costs(self):

        logger.info(
        'Mercado Livre Costs | '
        'Starting the extraction of necessary IDs from the Order.'
        )
        async with SessionLocal() as session:
            repository = OrderItem(session=session)
            offset: int = 7
            more_page: bool = True
            item_costs = []
            while more_page:
                orders = await repository.item_without_commission_meli(
                    offset=offset
                )

                for order in orders:
                    order_items = await repository.searching_order_item(
                        order_id=order[0]
                    )
                    print(order)
                    print(order_items)
                    costs = self.get_commision_ship_cost(
                        meli_order=order[1],
                        order_id=order[0],
                        order_items=order_items
                    )
                    if costs is None:
                        continue
                    for item in costs:
                        if order[2] == 'Mercado Envios Flex':
                            shipping: float = 12.99
                            item.item_shipping = shipping
                            item_costs.append(item)
                        else:
                            item_costs.append(item)

                if len(orders) < 100:
                    more_page = False
                else:
                    offset += 100

            await repository.update_shipping_commission(item_costs)

            await session.commit()

    def get_commision_ship_cost(
        self,
        meli_order,
        order_id,
        order_items
        ):

        url: str = endpoint_order(id_venda=meli_order)

        logger.info('Mercado Livre Costs | EndPoint order %s', url)

        response: IdsPedidoML = self.extraindo_packid_payid(url=url)

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

                    response_idvenda: PageResult = (
                        self.service_base.organiza_get_request(url=url)
                    )

                    commission = response_idvenda.data['order_items'][0][
                        'sale_fee'
                    ]

                    ship_cost = self.get_ship_cost(
                        response_idvenda.data['shipping']['id']
                    )

                    for item in order_items:
                        if item[2] == response_idvenda.data['order_items'][0][
                                        'item'
                                        ]['seller_sku']:
                            commission_ship_cost.append(
                                ItemComissionShip(
                                order_item_id=item[0],
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
                    order_item_id=order_items[0][0],
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
