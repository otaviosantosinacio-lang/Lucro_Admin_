import logging

from lucro_admin.infra.executa_database import (
    consultadb_com_parametros,
    consultageral,
)

logger = logging.getLogger('lucroadmin.infra.produtos')


class Produtos:
    def consulta_custo(self, SKU):
        logger.info('Produtos Repo | Iniciando consulta do preço de custo')
        query = 'SELECT preco_custo FROM produtos WHERE sku = %s'
        preco_custo = consultadb_com_parametros(execute=query, params=(SKU,))
        return preco_custo

    def consulta_todos_produtos(self):
        logger.info(
            'Produtos Repo | Iniciando a consulta no banco de dados de todos'
            ' os produtos'
        )
        query = 'SELECT * FROM produtos'
        produtos = consultageral(execute=query)

        return produtos
