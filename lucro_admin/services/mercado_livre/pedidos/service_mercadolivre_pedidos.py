import logging

from lucro_admin.core.entities_pedidos import (
    ComissaoFrete,
    IdsPedidoML,
    PedidoCompleto,
    PedidoseProdutosCompletos,
    ProdutoCompleto,
    ResultadoPagina,
)
from lucro_admin.services.mercado_livre.pedidos.service_mercadolivre_base import (
    BaseHTTPMercadoLivre,
)
from lucro_admin.services.mercado_pago.service_mercadopago import (
    MercadoPagoCustos,
)

logger = logging.getLogger('lucroadmin.services.mercadolivrepedidos')


class ExtraiCustoMercadoLivre:
    def __init__(self, access_token, adapt_pedido):
        self.access_token = access_token
        self.adapt_pedido = adapt_pedido
        self.service_base = BaseHTTPMercadoLivre(
            self.adapt_pedido, self.access_token
        )
        self.mercado_pago = MercadoPagoCustos()

    def endpoint_order(self, id_venda: int) -> str:

        url = f'https://api.mercadolibre.com/orders/{id_venda}'
        return url

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

    def extraindo_custos(self, pedidos):

        logger.info(
            'Mercado Livre IDs | Iniciando a extração de ids necessários da Ordem'
        )

        pedidos_completo = []
        produtos_completos = []

        for pedido in pedidos.pedidos:
            if pedido.nome_loja in ('Mercado Livre Full', 'Mercado Livre'):
                id_venda: int = pedido.id_mkt
                url: str = self.endpoint_order(id_venda=id_venda)
                logger.info('Mercado Livre Custos | EndPoint da ordem %s', url)
                response: IdsPedidoML = self.extraindo_packid_payid(url=url)
                logger.info('Mercado Livre Custos | Retorno -> %s', response)
                if response.pack_id != None:
                    ids = self.get_ids_por_pack(id_pack=response.pack_id)
                    comissao_total = frete_total = 0.0
                    if ids['status'] == 'ok':
                        for id in ids['ids']:
                            id_venda = id['id']
                            url: str = self.endpoint_order(id_venda=id_venda)
                            response_id: ResultadoPagina = (
                                self.service_base.organiza_get_request(url=url)
                            )
                            comissao = response_id.data['order_items'][0][
                                'sale_fee'
                            ]
                            id_pay = response_id.data['payments'][0]['id']
                            frete: float = (
                                self.mercado_pago.get_merchant_orders(
                                    id_pay=id_pay
                                )
                            )
                            for produto in pedidos.impostos_produto:
                                if pedido.id_bling == produto.id_bling:
                                    if (
                                        response_id.data['order_items'][0][
                                            'item'
                                        ]['seller_sku']
                                        == produto.sku
                                    ):
                                        produto_completo = ProdutoCompleto(
                                            id_bling=produto.id_bling,
                                            situacao_pedido=produto.situacao_pedido,
                                            sku=produto.sku,
                                            quantidade=produto.quantidade,
                                            preco_custo=produto.preco_custo,
                                            valor=produto.valor,
                                            icms=produto.icms,
                                            pis=produto.pis,
                                            cofins=produto.cofins,
                                            difal=produto.difal,
                                            fcp=produto.fcp,
                                            total_imposto=produto.total,
                                            frete=frete,
                                            comissao=comissao,
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
                else:
                    comissao = response.comissao
                    response.geral['payments'][0]['id']
                    frete: float = self.mercado_pago.get_merchant_orders(
                        id_pay=response.pay_id
                    )
                    if pedido.servico_trans == 'Mercado Envios Flex':
                        frete = 12.99
                        custos_venda: ComissaoFrete = ComissaoFrete(
                            id_bling=pedido.id_bling,
                            comissao=comissao,
                            frete=frete,
                        )
                    else:
                        custos_venda: ComissaoFrete = ComissaoFrete(
                            id_bling=pedido.id_bling,
                            comissao=comissao,
                            frete=frete,
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

    def endpoint_pack(self, id_pack: int) -> str:

        url = f'https://api.mercadolibre.com/packs/{id_pack}'
        return url

    def get_ids_por_pack(self, id_pack):

        url = self.endpoint_pack(id_pack=id_pack)

        response = self.service_base.organiza_get_request(url=url)

        if response.status == 'ok':
            ids_venda = response.data['orders']
            return {'status': 'ok', 'ids': ids_venda}
