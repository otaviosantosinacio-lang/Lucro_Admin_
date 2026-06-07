import logging
import typing
from datetime import datetime

from lucro_admin.infra.executa_database import (
    consultadb,
    consultageral,
    updatecredentdb,
)

logger = logging.getLogger('lucroadmin.infra.credenciais_bling')


class CredenciaisDB_bling:
    def get_client_id(self) -> str:
        logger.info('Bling Credencial | Iniciando consulta do client_id')
        execute = 'SELECT client_id FROM blingapi'
        client_id: str = consultadb(execute)
        return client_id

    def get_client_secret(self) -> str:
        logger.info('Bling Credencial | Iniciando consulta do client_secret')
        execute = 'SELECT client_secret FROM blingapi'
        client_secret: str = consultadb(execute)
        return client_secret

    def get_access_token(self) -> str:
        logger.info('Bling Credencial | Iniciando consulta do access_token')
        execute = 'SELECT access_token FROM blingapi'
        access_token: str = consultadb(execute)
        return access_token

    def get_refresh_token(self) -> str:
        logger.info('Bling Credencial | Iniciando consulta do refresh_token')
        execute = 'SELECT refresh_token FROM blingapi'
        refresh_token: str = consultadb(execute)
        return refresh_token

    def get_expire(self) -> typing.Any | None:
        logger.info('Bling Credencial | Iniciando consulta do expire')
        execute = 'SELECT expire FROM blingapi'
        expire = consultadb(execute)
        return expire

    def salva_token(self, access, refresh, expire) -> bool:
        logger.info('Bling Credencial | Iniciando o update das credenciais')
        execute = (
            'UPDATE blingapi SET  access_token=%s, refresh_token=%s, expire=%s'
        )
        params = (access, refresh, expire)
        update_bling = updatecredentdb(execute, params)
        return update_bling


class DadosGerais:
    def situacoes(self):
        logger.info('Consulta Dados situacoes | Iniciando busca das situacoes')
        execute = 'SELECT * FROM situacaobling'
        situacoes = consultageral(execute)

        return situacoes

    def data_ultimo_pedido(self) -> datetime:
        logger.info(
            'Consulta Dados data ultimo pedido | Iniciando busca da data do ultimo pedido'
        )
        execute = """SELECT data 
                     FROM pedidos_venda
                     ORDER BY data DESC
                     LIMIT 1"""
        data: datetime = consultadb(execute)
        logger.info(
            'Consulta Dados data ultimo pedido | Retorno da consulta %s', data
        )
        return data
