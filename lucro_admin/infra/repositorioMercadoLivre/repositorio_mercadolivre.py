import logging
import typing

from lucro_admin.infra.executa_database import consultadb, updatecredentdb

logger = logging.getLogger('lucroadmin.infra.credenciais_mercadolivre')


class CredenciaisMercadoLivre:
    def get_client_id(self) -> str:
        logger.info(
            'Mercado Livre Credencial | Iniciando consulta do client_id'
        )
        execute = 'SELECT client_id FROM mlapi'
        client_id: str = consultadb(execute)
        return client_id

    def get_client_secret(self) -> str:
        logger.info(
            'Mercado Livre Credencial | Iniciando consulta do client_secret'
        )
        execute = 'SELECT client_secret FROM mlapi'
        client_secret: str = consultadb(execute)
        return client_secret

    def get_access_token(self) -> str:
        logger.info(
            'Mercado Livre Credencial | Iniciando consulta do access_token'
        )
        execute = 'SELECT access_token FROM mlapi'
        access_token: str = consultadb(execute)
        return access_token

    def get_refresh_token(self) -> str:
        logger.info(
            'Mercado Livre Credencial | Iniciando consulta do refresh_token'
        )
        execute = 'SELECT refresh_token FROM mlapi'
        refresh_token: str = consultadb(execute)
        return refresh_token

    def get_expire(self) -> typing.Any | None:
        logger.info('Mercado Livre Credencial | Iniciando consulta do expire')
        execute = 'SELECT expire FROM mlapi'
        expire = consultadb(execute)
        return expire

    def salva_token(self, access, refresh, expire) -> bool:
        logger.info(
            'Mercado Livre Credencial | Iniciando o update das credenciais'
        )
        execute = (
            'UPDATE mlapi SET  access_token=%s, refresh_token=%s, expire=%s'
        )
        params = (access, refresh, expire)
        update_bling = updatecredentdb(execute, params)
        return update_bling
