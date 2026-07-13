import logging
from typing import Any

from lucro_admin.core.entities_pedidos import (
    ComissaoFrete,
    IdsPedidoML,
    PedidoCompleto,
    PedidoseProdutosCompletos,
    ProdutoCompleto,
    ResultadoPagina,
    ShipCommission,
    SaleCosts
)
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

        response: ResultadoPagina = self.service_base.organiza_get_request(
            url=url
        )
        if response.status == 'ok':
            return IdsPedidoML(
                comissao=response.data['order_items'][0]['sale_fee'],
                pay_id=response.data['payments'][0]['id'],
                pack_id=response.data['pack_id'],
                geral=response.data,
            )

    def get_sale_costs(self, pedidos):

        logger.info(
        'Mercado Livre IDs | Iniciando a extração de ids necessários da Ordem'
        )

        pedidos_completo = []
        produtos_completos = []
        name_market = ['Mercado Livre Full', 'Mercado Livre']

        for pedido in pedidos.pedidos:
            breakpoint()
            if pedido.nome_loja not in name_market:
                continue
            costs = self.get_commision_ship_cost(pedido)
            for product in pedidos.impostos_produto:
                if pedido.id_bling == product.id_bling:
                    for product_cost in costs:
                        if product_cost.sku == product.sku:
                            produto_completo = ProdutoCompleto(
                                id_bling=product.id_bling,
                                situacao_pedido=product.situacao_pedido,
                                sku=product.sku,
                                quantidade=product.quantidade,
                                preco_custo=product.preco_custo,
                                valor=product.valor,
                                icms=product.icms,
                                pis=product.pis,
                                cofins=product.cofins,
                                difal=product.difal,
                                fcp=product.fcp,
                                total_imposto=product.total,
                                frete=product_cost.ship_cost,
                                comissao=product_cost.commission,
                            )
                            produtos_completos.append(
                                produto_completo
                            )
                frete_total += frete
                comissao_total += comissao
                if pedido.servico_trans == 'Mercado Envios Flex':
                    frete = 12.99
                    custos_venda: ComissaoFrete = ComissaoFrete(
                        id_bling=pedido.id_bling,
                        comissao=comissao_total,
                        frete=frete,
                    )
                else:
                    custos_venda: ComissaoFrete = ComissaoFrete(
                        id_bling=pedido.id_bling,
                        comissao=comissao_total,
                        frete=frete_total,
                    )
            lucro = (
                pedido.valor_pedido
                - pedido.custo_produto
                - pedido.total
                - custos_venda.comissao
                - custos_venda.frete
            )
            pedido_total: PedidoCompleto = PedidoCompleto(
                id_bling=pedido.id_bling,
                num_bling=pedido.num_bling,
                situacao=pedido.situacao,
                id_mkt=pedido.id_mkt,
                data=pedido.data,
                nome_loja=pedido.nome_loja,
                nf_id=pedido.nf_id,
                valor_pedido=pedido.valor_pedido,
                icms=pedido.icms,
                pis=pedido.pis,
                cofins=pedido.cofins,
                difal=pedido.difal,
                fcp=pedido.fcp,
                total_imposto=pedido.total,
                custo_produto=pedido.custo_produto,
                comissao=custos_venda.comissao,
                frete=custos_venda.frete,
                lucro=lucro,
            )
            pedidos_completo.append(pedido_total)
        return PedidoseProdutosCompletos(
            pedidos=pedidos_completo, produtos=produtos_completos
        )

    def get_commision_ship_cost(self, pedido) -> SaleCosts:

        id_venda: int = pedido.id_mkt
        url: str = endpoint_order(id_venda=id_venda)
        logger.info('Mercado Livre Custos | EndPoint da ordem %s', url)
        response: IdsPedidoML = self.extraindo_packid_payid(url=url)
        logger.info('Mercado Livre Custos | Retorno -> %s', response)
        commission_ship_cost: SaleCosts | Any = []
        if response.pack_id != None:
            ids = self.get_ids_por_pack(id_pack=response.pack_id)
            if ids['status'] == 'ok':
                for id in ids['ids']:
                    id_venda = id['id']
                    url: str = endpoint_order(id_venda=id_venda)
                    response_idvenda: ResultadoPagina = (
                        self.service_base.organiza_get_request(url=url)
                    )
                    commission = response_idvenda.data['order_items'][0][
                        'sale_fee'
                    ]
                    ship_cost = self.get_ship_cost(
                        response_idvenda.data['shipping']['id']
                    )
                    commission_ship_cost.append(
                        ShipCommission(
                            id=id_venda,
                            commission=commission,
                            ship_cost=ship_cost,
                            sku=response_idvenda.data['order_items'][0][
                                        'item'
                                        ]['seller_sku']
                        )
                    )
        else:
            commission = response.comissao
            ship_cost: float = self.get_ship_cost(
                        response.geral['shipping']['id']
                        )
            commission_ship_cost.append(
                ShipCommission(
                    id=id_venda,
                    commission=commission,
                    ship_cost=ship_cost,
                    sku=response.geral['order_items'][0][
                                'item'
                                ]['seller_sku'])
            )
        return commission_ship_cost

    def get_ship_cost(self, ship_id):

        url: str = f'https://api.mercadolibre.com/shipments/{ship_id}/costs'
        response = self.service_base.organiza_get_request(url=url)
        custo_frete = response.data['senders'][0]['cost']
        return custo_frete

    def get_ids_por_pack(self, id_pack):

        url = endpoint_pack(id_pack=id_pack)

        response = self.service_base.organiza_get_request(url=url)

        if response.status == 'ok':
            ids_venda = response.data['orders']
            return {'status': 'ok', 'ids': ids_venda}
