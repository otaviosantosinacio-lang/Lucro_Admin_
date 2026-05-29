from lucro_admin.infra.executa_database import executa_insert_pedidos
import logging
from datetime import datetime, date
import typing

logger = logging.getLogger('lucroadmin.infra.pedidos')


class InsertPedidos:
    def insert_pedidos(self, pedidos):
        logger.info('Pedidos Repo | Iniciando a inserção dos pedidos')
        for pedido in pedidos:
            query = """
            INSERT INTO pedidos_venda 
            (id_bling, num_bling, situacao, id_nf, 
             id_loja, loja, data, icms, 
             pis, cofins, icms_dest, fcp, 
             total_imposto, frete, comissao, 
             lucro, custo_total_produtos, valor_pedido) VALUES %s"""
            values = [
                (
                    pedido.id_bling,
                    pedido.num_bling,
                    pedido.situacao,
                    pedido.nf_id,
                    pedido.id_mkt,
                    pedido.nome_loja,
                    pedido.data,
                    pedido.icms,
                    pedido.pis,
                    pedido.cofins,
                    pedido.difal,
                    pedido.fcp,
                    pedido.total_imposto,
                    pedido.frete,
                    pedido.comissao,
                    pedido.lucro,
                    pedido.custo_produto,
                    pedido.valor_pedido,
                )
            ]
            insert = executa_insert_pedidos(execute=query, params=values)
