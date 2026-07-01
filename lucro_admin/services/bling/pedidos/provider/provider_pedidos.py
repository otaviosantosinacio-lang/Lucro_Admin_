import logging

from lucro_admin.core.entities_pedidos import (
    Dados_Pedido_imposto,
    PedidoseImpostos,
    ResultadoGetDetalhes,
    ResultadoGetPaginas,
)
from lucro_admin.core.imposto.calcula_imposto import CalculadoraDeImposto
from lucro_admin.services.bling.pedidos.parse_xml import ParseXML
from lucro_admin.services.bling.pedidos.provider.provider import (
    PedidosProvider,
)
from lucro_admin.services.bling.pedidos.service_bling_pedidos import (
    Atendidos,
    ProcessaId,
)

logger = logging.getLogger('lucroadmin.services')


class PedidosProviderBling(PedidosProvider):
    """

    PedidosProviderBling -> Orquestração do fluxo de pedidos Bling

    """

    def __init__(self, adapt_pedidos, repo_pedidos, access_token) -> None:
        self.adapt_pedidos = adapt_pedidos
        self.repo_pedidos = repo_pedidos
        self.access_token = access_token
        self.service_id_pag = Atendidos(
            self.access_token, self.adapt_pedidos, repo_pedidos
        )
        self.service_processa = ProcessaId(
            self.access_token, self.adapt_pedidos, self.repo_pedidos
        )
        self.service_xml = ParseXML(self.access_token, self.adapt_pedidos)
        self.calculadora = CalculadoraDeImposto()

    def id_pag(self) -> ResultadoGetPaginas:
        """
        Docstring para id_pag

        :param self: Objeto
        :return: ids_bling obtidos
        :rtype: ResultadoGetPaginas

        """
        return self.service_id_pag.get_id_por_pag()

    def processa_ids(self):

        ids: ResultadoGetPaginas = self.id_pag()
        logger.info('Bling Provider Pedido | Lista retornada %s', ids)
        situacao = ids.situacao
        processa_pedido: ResultadoGetDetalhes = (
            self.service_processa.get_id_detalhes(
                ids_list=ids.vendas_id, situacao=situacao
            )
        )
        imposto_produto = []
        pedidos_imposto = []

        for pedido in processa_pedido.pedidos:
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
                    imposto.produto_imposto,
                    imposto.venda_imposto,
                )
                for produto in imposto.produto_imposto:
                    imposto_produto.append(produto)

            else:
                logger.info(
                    'Bling Provider Pedido |'
                    ' Calculando custos fiscais com a calculadora de impostos'
                )
                imposto = self.calculadora.calculadora_de_tributos(
                    itens=pedido.itens,
                    id_bling=pedido.id_bling,
                    sit=situacao,
                    uf_dest=pedido.uf_dest,
                )
                logger.info(
                    'Bling Provider Pedido |'
                    ' Impostos retornados por produto da calculadora->'
                    ' %s -> Impostos da venda retornado da calculadora -> %s',
                    imposto.produto_imposto,
                    imposto.venda_imposto,
                )
                for produto in imposto.produto_imposto:
                    imposto_produto.append(produto)
            PedidocomImposto = Dados_Pedido_imposto(
                id_bling=pedido.id_bling,
                num_bling=pedido.num_bling,
                situacao=situacao,
                id_mkt=pedido.id_mkt,
                data=pedido.data,
                nome_loja=pedido.nome_loja,
                nf_id=pedido.nf_id,
                valor_pedido=pedido.valor_pedido,
                servico_trans=pedido.servico_trans,
                icms=imposto.venda_imposto.icms,
                pis=imposto.venda_imposto.pis,
                cofins=imposto.venda_imposto.cofins,
                difal=imposto.venda_imposto.difal,
                fcp=imposto.venda_imposto.fcp,
                custo_produto=imposto.venda_imposto.custo,
                total=imposto.venda_imposto.total,
            )
            pedidos_imposto.append(PedidocomImposto)
        return PedidoseImpostos(
            pedidos=pedidos_imposto, impostos_produto=imposto_produto
        )
