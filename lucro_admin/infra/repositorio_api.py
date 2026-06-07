import logging

from lucro_admin.infra.executa_database import (
    consultadb_multiplos_retornos,
)

logger = logging.getLogger('lucroadmin.infra.api')


def consulta_por_data(data_inicial, data_final):
    logger.info('API | Iniciando busca por data | Pedidos Venda')
    query = """SELECT * FROM pedidos_venda WHERE data BETWEEN %s AND %s"""
    params = (data_inicial, data_final)
    pedidos = consultadb_multiplos_retornos(execute=query, params=params)
    return pedidos
