import logging
from datetime import datetime

from lucro_admin.services.providers.provider import TokenProvider
from lucro_admin.services.mercado_livre.tokens.service_mercadolivre_credenciais import (
    oAuthRefreshMercadoLivre,
)

logger = logging.getLogger('lucroadmin.services.provider')


class MLProvider(TokenProvider):
    def __init__(self, repositorio, adapter_refresh):
        self.repositorio = repositorio
        self.adapter_refresh = adapter_refresh

    def get_access_token(self) -> str:
        logger.info(
            'Mercado Livre Provider | Buscando no Banco de Dados o access token.'
        )
        return self.repositorio.get_access_token()

    def get_expire(self) -> datetime:
        logger.info(
            'Mercado Livre Provider | Buscando no Banco de Dados o expire.'
        )
        return self.repositorio.get_expire()

    def use_refresh_token(self) -> str | None:
        logger.info(
            'Mercado Livre Provider | Iniciando o fluxo de uso do refresh token.'
        )
        fluxo_refresh = oAuthRefreshMercadoLivre(
            self.repositorio, self.adapter_refresh
        )
        access_token: str | None = fluxo_refresh.fluxo_refresh_token()
        logger.info(
            'Mercado Livre Provider | Fluxo do refresh token finalizado.'
        )
        return access_token
