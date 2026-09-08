import logging
from datetime import datetime

from lucro_admin.services.providers.provider import TokenProvider
from lucro_admin.services.tiny.credentials.tiny_oauth import (
    oAuthRefreshTiny,
)
from lucro_admin.settings import TinySettings

logger = logging.getLogger('lucroadmin.services.provider')


class TinyProvider(TokenProvider):
    def __init__(self, adapter_refresh):
        self.credentials = TinySettings()
        self.adapter_refresh = adapter_refresh

    def get_access_token(self) -> str:
        logger.info(
            'Tiny Provider | Searching the Database for the access token.'
        )
        return self.credentials.ACCESS_TOKEN

    def get_expire(self) -> datetime:
        logger.info(
            'Tiny Provider | Searching the Database for the access tokens'
            ' expiration.'
        )
        expire_str = self.credentials.EXPIRE_ACCESS
        expire_date = datetime.fromisoformat(expire_str)
        return expire_date

    def use_refresh_token(self) -> str:
        logger.info(
            'Tiny Provider | Starting the refresh token usage flow.'
        )
        refresh_flow = oAuthRefreshTiny(
            self.adapter_refresh
        )
        access_token: str = refresh_flow.refresh_token_flow_tiny()
        logger.info('Tiny Provider | Refresh token flow completed.')
        return access_token
