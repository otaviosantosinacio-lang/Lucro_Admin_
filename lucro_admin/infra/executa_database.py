import logging
from typing import Any

from psycopg2.extras import execute_values

from lucro_admin.infra.conexao_DB import conecta_DB

logger = logging.getLogger('lucroadmin.infra.executa_database')


def consultadb(execute: str) -> Any:
    """
    consultadb -> Consulta no banco de dados para dados especificos mediante
    a Query informada

    :param execute: Query para consulta no banco de dados.
    :type execute: str

    """
    try:
        with conecta_DB() as conn:
            with conn.cursor() as cur:
                cur.execute(execute)
                result = cur.fetchone()
                logger.info('Executa Data Base | Query -> %s', execute)
                if result:
                    param = result[0]
                    logger.debug('Executa Data Base | Consulta concluida')
                    return param
                else:
                    logger.critical(
                        'Executa Data Base | Erro o SELECT não retornou nada |'
                        ' Query -> %s',
                        execute,
                    )
                    return None
    except Exception:
        logger.exception(
            'Executa Data Base | Erro na consulta usando SELECT | Query -> %s',
            execute,
        )
        return None


def consultadb_com_parametros(
    execute: str, params: tuple | None = None
) -> Any:
    """
    consultadb -> Consulta no banco de dados para dados especificos mediante
    a Query informada

    :param execute: Query para consulta no banco de dados.
    :type execute: str

    """
    try:
        with conecta_DB() as conn:
            with conn.cursor() as cur:
                cur.execute(execute, params)
                result = cur.fetchone()
                logger.info('Executa Data Base | Query -> %s', execute)
                if result:
                    param = result[0]
                    logger.debug('Executa Data Base | Consulta concluida')
                    return param
                else:
                    logger.critical(
                        'Executa Data Base | Erro o SELECT não retornou nada |'
                        ' Query -> %s',
                        execute,
                    )
                    return None
    except Exception:
        logger.exception(
            'Executa Data Base | Erro na consulta usando SELECT | Query -> %s',
            execute,
        )
        return None


def consultageral(execute: str):
    """
    consultageral

    :param execute: Query para retornar diversos dados na consulta ao banco
    de dados
    :type execute: str
    """
    try:
        with conecta_DB() as conn:
            with conn.cursor() as cur:
                cur.execute(execute)
                result = cur.fetchall()
                logger.info('Executa Data Base | Query -> %s', execute)
                if result:
                    param = result
                    logger.debug('Executa Data Base | Consulta concluida')
                    return param
                else:
                    logger.critical(
                        'Executa Data Base | Erro o SELECT não retornou nada '
                        '| Query -> %s',
                        execute,
                    )
                    return None
    except Exception:
        logger.exception(
            'Executa Data Base | Erro na consulta usando SELECT | Query -> %s',
            execute,
        )
        return None


def updatecredentdb(execute: str, params) -> bool:
    """
    updatecredentdb -> Atualização das credenciais salvas no banco de dados.

    :param execute: Query para salvar as credênciais.
    :type execute: str
    :param params: Credenciais que serão atualizadas.
    :return: Se atualização foi concluida ou não.
    :rtype: bool

    """
    try:
        with conecta_DB() as conn:  # type: ignore
            # Declarando o cursor/executor da conexão
            with conn.cursor() as cur:
                # Contagem das linhas inseridas através do comando SQL
                cur.execute(execute, params)
                logger.info('Executa Data Base | Update finalizado')
                return True

    except Exception:
        logger.critical(
            'Executa Data Base | Erro no Update | Query -> %s', execute
        )
        return False


def executa_insert_pedidos(execute: str, params):
    try:
        with conecta_DB() as conn:
            with conn.cursor() as cur:
                execute_values(cur=cur, sql=execute, argslist=params)
                logger.info(
                    'Executa Data Base | Insert finalizado com sucesso'
                )
                return True
    except Exception:
        logger.exception(
            'Executa Data Base | Erro no INSERT | Query -> %s', execute
        )
        return None


def consultadb_multiplos_retornos(
    execute: str, params: tuple | None = None
) -> Any:
    """
    consultadb -> Consulta no banco de dados para dados especificos mediante
    a Query informada

    :param execute: Query para consulta no banco de dados.
    :type execute: str

    """
    try:
        with conecta_DB() as conn:
            with conn.cursor() as cur:
                cur.execute(execute, params)
                result = cur.fetchall()
                logger.info('Executa Data Base | Query -> %s', execute)
                if result:
                    param = result
                    logger.debug('Executa Data Base | Consulta concluida')
                    return param
                else:
                    logger.critical(
                        'Executa Data Base | Erro o SELECT não retornou nada'
                        ' | Query -> %s',
                        execute,
                    )
                    return None
    except Exception:
        logger.exception(
            'Executa Data Base | Erro na consulta usando SELECT | Query -> %s',
            execute,
        )
        return None
