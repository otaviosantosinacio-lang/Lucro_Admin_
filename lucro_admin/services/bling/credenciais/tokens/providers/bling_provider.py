import logging
from lucro_admin.services.providers.provider import TokenProvider
from datetime import datetime
from lucro_admin.services.bling.credenciais.service_bling_credenciais import (
    oAuthRefreshBling,
)

logger = logging.getLogger('lucroadmin.services.provider')


class BlingProvider(TokenProvider):
    def __init__(self, repositorio, adapter_refresh):
        self.repositorio = repositorio
        self.adapter_refresh = adapter_refresh

    def get_access_token(self) -> str:
        logger.info(
            'Bling Provider | Buscando no Banco de Dados o access token.'
        )
        return self.repositorio.get_access_token()

    def get_expire(self) -> datetime:
        logger.info('Bling Provider | Buscando no Banco de Dados o expire.')
        return self.repositorio.get_expire()

    def use_refresh_token(self) -> str:
        logger.info(
            'Bling Provider | Iniciando o fluxo de uso do refresh token.'
        )
        fluxo_refresh = oAuthRefreshBling(
            self.repositorio, self.adapter_refresh
        )
        access_token: str = fluxo_refresh.fluxo_refresh_token()
        logger.info('Bling Provider | Fluxo do refresh token finalizado.')
        return access_token
