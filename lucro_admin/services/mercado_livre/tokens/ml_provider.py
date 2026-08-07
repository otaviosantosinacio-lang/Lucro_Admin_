import logging
from datetime import datetime

from lucro_admin.services.mercado_livre.tokens.service_mercadolivre_credenciais import (
    oAuthRefreshMercadoLivre,
)
from lucro_admin.services.providers.provider import TokenProvider
from lucro_admin.settings import MeliSettings

logger = logging.getLogger('lucroadmin.services.provider')


class MLProvider(TokenProvider):
    def __init__(self, adapter_refresh):
        self.credentials = MeliSettings()
        self.adapter_refresh = adapter_refresh

    def get_access_token(self) -> str:
        logger.info(
        'Mercado Livre Provider | Buscando no Banco de Dados o access token.'
        )
        return self.credentials.ACCESS_TOKEN

    def get_expire(self) -> datetime:
        logger.info(
            'Mercado Livre Provider | Buscando no Banco de Dados o expire.'
        )
        expire_str = self.credentials.EXPIRE
        expire_date = datetime.fromisoformat(expire_str)
        return expire_date

    def use_refresh_token(self) -> str | None:
        logger.info(
        'Mercado Livre Provider | Iniciando o fluxo de uso do refresh token.'
        )
        fluxo_refresh = oAuthRefreshMercadoLivre(
            self.adapter_refresh
        )
        access_token: str | None = fluxo_refresh.fluxo_refresh_token()
        logger.info(
            'Mercado Livre Provider | Fluxo do refresh token finalizado.'
        )
        return access_token
