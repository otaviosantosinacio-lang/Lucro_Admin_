from infra.executa_database import executa_insert_pedidos
import logging
from datetime import datetime, date
import typing

logger = logging.getLogger('lucroadmin.infra.pedidos')


class InsertPedidosProdutos:
    def insert_pedidos_produtos(self, pedido_produto):
        logger.info('Pedidos Produtos Repo | Iniciando a inserção dos pedidos')
        for pedido in pedido_produto:
            query = """
            INSERT INTO pedidos_produtos 
            (id_bling_venda, situacao_venda, sku, qnt, 
             valor, icms, pis, cofins,
             icms_dest, fcp, total_imposto, 
             comissao, frete, preco_custo) VALUES %s"""
            values = [
                (
                    pedido.id_bling,
                    pedido.situacao_pedido,
                    pedido.sku,
                    pedido.quantidade,
                    pedido.valor,
                    pedido.icms,
                    pedido.pis,
                    pedido.cofins,
                    pedido.difal,
                    pedido.fcp,
                    pedido.total_imposto,
                    pedido.comissao,
                    pedido.frete,
                    pedido.preco_custo,
                )
            ]
            insert = executa_insert_pedidos(execute=query, params=values)
