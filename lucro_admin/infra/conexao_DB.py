import logging
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

logger = logging.getLogger('lucroadmin.infra.DataBase')


def conecta_DB():
    """
    conecta_DB -> Estabelece conexão com o Banco de Dados
    """
    try:
        logger.debug('Data Base | Iniciando conexão')
        # Carregar variaveis do arquivo .env
        BASE_DIR = Path(__file__).resolve().parents[1]
        load_dotenv(BASE_DIR / 'database.env')
        # Aqui declaro a url que me dará acesso ao Db
        conn_string = os.getenv('DATABASE')
        logger.debug('Data Base | Conexaão bem sucedida')
        return psycopg2.connect(conn_string)
    except:
        logger.exception('Data Base | ERRO: Conexão mal sucedida')
        return
