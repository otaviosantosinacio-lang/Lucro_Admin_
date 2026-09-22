import logging
from datetime import datetime

from lucro_admin.services.bling.credentials.service_bling_credentials import (
    oAuthRefreshBling,
)
from lucro_admin.services.providers.provider import TokenProvider
from lucro_admin.settings import BlingSettings

logger = logging.getLogger('lucroadmin.services.provider')


class BlingProvider(TokenProvider):
    def __init__(self, adapter_refresh):
        self.credentials = BlingSettings()
        self.adapter_refresh = adapter_refresh

    def get_access_token(self) -> str:
        logger.info(
            'Bling Provider | Searching the Database for the access token.'
        )
        return self.credentials.ACCESS_TOKEN

    def get_expire(self) -> datetime:
        logger.info(
            'Bling Provider | Searching the Database for the access tokens'
            ' expiration.'
        )
        expire_str = self.credentials.EXPIRE
        expire_date = datetime.fromisoformat(expire_str)
        return expire_date

    def use_refresh_token(self) -> str:
        logger.info(
            'Bling Provider | Starting the refresh token usage flow.'
        )
        refresh_flow = oAuthRefreshBling(
            self.adapter_refresh
        )
        access_token: str = refresh_flow.refresh_token_flow_bling()
        logger.info('Bling Provider | Refresh token flow completed.')
        return access_token
