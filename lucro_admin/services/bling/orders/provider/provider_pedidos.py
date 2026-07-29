import logging

from lucro_admin.core.entities_pedidos import (
    Dados_Pedido_imposto,
    GetDetailsResult,
    GetPagesResult,
    PedidoseImpostos,
)
from lucro_admin.core.imposto.tax_calculator import TaxCalculator
from lucro_admin.services.bling.orders.provider.provider import (
    PedidosProvider,
)
from lucro_admin.services.bling.orders.service_bling_orders import (
    Attended,
    ProcessaId,
)
from lucro_admin.services.parse_xml import ParseXML

logger = logging.getLogger('lucroadmin.services')


class PedidosProviderBling(PedidosProvider):
    """

    PedidosProviderBling -> Orquestração do fluxo de pedidos Bling

    """

    def __init__(self, adapt_pedidos, repo_pedidos, access_token) -> None:
        self.adapt_pedidos = adapt_pedidos
        self.repo_pedidos = repo_pedidos
        self.access_token = access_token
        self.service_id_pag = Attended(
            self.access_token, self.adapt_pedidos, repo_pedidos
        )
        self.service_processa = ProcessaId(
            self.access_token, self.adapt_pedidos, self.repo_pedidos
        )
        self.service_xml = ParseXML(self.access_token, self.adapt_pedidos)
        self.calculadora = TaxCalculator()

    def id_pag(self) -> GetPagesResult:
        """
        Docstring para id_pag

        :param self: Objeto
        :return: ids_bling obtidos
        :rtype: ResultadoGetPaginas

        """
        return self.service_id_pag.get_id_by_page()

    def processa_ids(self):

        ids: GetPagesResult = self.id_pag()
        logger.info('Bling Provider Pedido | Lista retornada %s', ids)
        situacao = ids.situation
        processa_pedido: GetDetailsResult = (
            self.service_processa.get_id_detalhes(
                ids_list=ids.sales_id, situacao=situacao
            )
        )
        imposto_produto = []
        pedidos_imposto = []

        for pedido in processa_pedido.orders:
            logger.info('Bling Provider Pedido | Pedido %s', pedido)
            if pedido.nf_id > 0:
                logger.info(
                    'Bling Provider Pedido |'
                    ' Buscando dados fiscais da nf_id -> %s',
                    pedido.nf_id,
                )
                imposto = self.service_xml.get_xml(
                    pedido=pedido, situacao=situacao
                )
                logger.info(
                    'Bling Provider Pedido | '
                    'Impostos retornados por produto-> %s -> '
                    'Impostos da venda retornado -> %s',
                    imposto.product_tax,
                    imposto.sale_tax,
                )
                for produto in imposto.product_tax:
                    imposto_produto.append(produto)

            else:
                logger.info(
                    'Bling Provider Pedido |'
                    ' Calculando custos fiscais com a calculadora de impostos'
                )
                imposto = self.calculadora.tax_calculator(
                    items=pedido.items,
                    id_bling=pedido.id_bling,
                    sit=situacao,
                    uf_dest=pedido.uf_dest,
                )
                logger.info(
                    'Bling Provider Pedido |'
                    ' Impostos retornados por produto da calculadora->'
                    ' %s -> Impostos da venda retornado da calculadora -> %s',
                    imposto.product_tax,
                    imposto.sale_tax,
                )
                for produto in imposto.product_tax:
                    imposto_produto.append(produto)
            PedidocomImposto = Dados_Pedido_imposto(
                id_bling=pedido.id_bling,
                num_bling=pedido.num_bling,
                situacao=situacao,
                id_mkt=pedido.id_mkt,
                data=pedido.data,
                nome_loja=pedido.name_store,
                nf_id=pedido.nf_id,
                valor_pedido=pedido.value_sale,
                servico_trans=pedido.servico_trans,
                icms=imposto.sale_tax.icms,
                pis=imposto.sale_tax.pis,
                cofins=imposto.sale_tax.cofins,
                difal=imposto.sale_tax.difal,
                fcp=imposto.sale_tax.fcp,
                custo_produto=imposto.sale_tax.cost,
                total=imposto.sale_tax.total,
            )
            pedidos_imposto.append(PedidocomImposto)
        return PedidoseImpostos(
            pedidos=pedidos_imposto, impostos_produto=imposto_produto
        )
