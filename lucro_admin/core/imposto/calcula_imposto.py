import logging

from lucro_admin.core.entities_produtos import ConfigSku
from lucro_admin.core.imposto.entities_imposto import (
    ImpostosDaVenda,
    ItemPedido,
    ProdutoComImposto,
    RetornoImpostos,
)
from lucro_admin.core.imposto.regras_fiscais import icms_aliq, uf_sem_fcp
from lucro_admin.infra.repositorio_produtos import Produtos

logger = logging.getLogger('lucroadmin.core.calculadoraimpostos')


class CalculadoraDeImposto:
    """
    CalculadoraDeImposto

    Calcula de forma manual impostos para operações internas e interestaduais.
    Impostos calculados como ICMS, PIS, COFINS, DIFAL e FCP

    """

    def calculadora_de_tributos(
        self, itens, id_bling, sit, uf_dest
    ) -> RetornoImpostos:
        """
        calculadora_de_tributos

        Calculando de forma precisa os tributos de um venda, e retornando-os 
        de forma ordenada e formatada

        :param self:
        :param itens: Produtos do Pedido
        :param id_bling: Id único da venda, esse id é gerado pelo bling
        :param sit: Situação do pedido dentro do Bling
        :param uf_dest: Unidade Federativa de destino da venda
        :return: Retorno individualizado por produto e também totalizado 
        pela venda
        :rtype: RetornoImpostos
        """

        logger.info(
            'Calculadora de Tributos | Iniciando calculo de tributos dos ' \
            'itens do pedido'
        )

        produtos = Produtos()
        # Validando FCP e aliquotas pis e cofins
        sem_fcp = uf_sem_fcp(uf_dest)
        produtos_com_imposto = []
        aliq_pis = 1.65 / 100
        aliq_cofins = 7.6 / 100

        # Looping para passarmos por todos os itens da venda
        for item in itens:
            item_pedido = ItemPedido(
                codigo=item['codigo'],
                quantidade=item['quantidade'],
                valor=item['valor'],
            )
            # Configurando o SKU pois alguns veem com SKU não formatado
            # corretamente.
            sku = ConfigSku.configsku(item_pedido.codigo)
            icms = pis = cofins = difal = fcp = 0.0

            # Validando ser a venda é uma operação local ou interestadual
            if uf_dest == 'SP':
                logger.info(
                    'Calculadora de Tributos | UF de origem SP e UF destino %s' \
                    ' -> Caracteriza operação interna',
                    uf_dest,
                )
                icms = item_pedido.valor * (18 / 100)
                pis = (item_pedido.valor - icms) * aliq_pis
                cofins = (item_pedido.valor - icms) * aliq_cofins
            # Se for interestadual devemos validar se o estado destino faz
            # cobrança do fundo de combate a pobreza ou não.
            elif sem_fcp:
                logger.info(
                    'Calculadora de Tributos | UF de origem SP e UF destino %s' \
                    ' -> Caracteriza operação interestadual, mas a UF não tem' \
                    ' cobrança do FCP',
                    uf_dest,
                )
                aliq_dest_total = icms_aliq(uf_dest) / 100
                aliq_orig = 4 / 100
                aliq_dest = aliq_dest_total - aliq_orig
                icms = item_pedido.valor * aliq_orig
                difal = item_pedido.valor * aliq_dest
                pis = (item_pedido.valor - (icms + difal)) * aliq_pis
                cofins = (item_pedido.valor - (icms + difal)) * aliq_cofins

            else:
                logger.info(
                    'Calculadora de Tributos | UF de origem SP e UF destino %s' \
                    ' -> Caracteriza operação interestadual, mas a UF tem' \
                    ' cobrança do FCP',
                    uf_dest,
                )
                aliq_dest_total = icms_aliq(uf_dest) / 100
                aliq_orig = 4 / 100
                aliq_fcp = 2 / 100
                aliq_dest = aliq_dest_total - aliq_orig
                icms = item_pedido.valor * aliq_orig
                difal = item_pedido.valor * aliq_dest
                pis = (item_pedido.valor - (icms + difal)) * aliq_pis
                cofins = (item_pedido.valor - (icms + difal)) * aliq_cofins
                fcp = item_pedido.valor * aliq_fcp

            total = icms + pis + cofins + difal + fcp

            preco_custo = produtos.consulta_custo(SKU=sku)
            preco_custo *= item_pedido.quantidade
            # Formatando os impostos do produto para um dataclass
            imposto_produto = ProdutoComImposto(
                id_bling=id_bling,
                situacao_pedido=sit,
                sku=sku,
                quantidade=item_pedido.quantidade,
                preco_custo=preco_custo,
                valor=item_pedido.valor,
                icms=icms,
                pis=pis,
                cofins=cofins,
                difal=difal,
                fcp=fcp,
                total=total,
            )
            logger.info(
                'Calculadora de Tributos | Tributo do produto calculado ->'
                ' %s\nMateus 22:21',
                imposto_produto,
            )
            produtos_com_imposto.append(imposto_produto)

        # Somando todos os impostos dos itens para totalizarmos os impostos 
        # da venda.
        impostos_venda = ImpostosDaVenda.soma_impostos(
            produtos_com_imposto, id_bling=id_bling
        )
        logger.info(
            'Calculadora de Tributos | Tributo da venda calculado ->'
            ' %s\nMateus 22:21',
            impostos_venda,
        )
        return RetornoImpostos(
            produto_imposto=produtos_com_imposto, venda_imposto=impostos_venda
        )
