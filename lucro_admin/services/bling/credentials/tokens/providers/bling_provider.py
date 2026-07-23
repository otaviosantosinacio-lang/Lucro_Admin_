import logging
from datetime import datetime

from lucro_admin.services.bling.credentials.service_bling_credentials import (
    oAuthRefreshBling,
)
from lucro_admin.services.providers.provider import TokenProvider

logger = logging.getLogger('lucroadmin.services.provider')


class BlingProvider(TokenProvider):
    def __init__(self, repository, adapter_refresh):
        self.repository = repository
        self.adapter_refresh = adapter_refresh

    def get_access_token(self) -> str:
        logger.info(
            'Bling Provider | Searching the Database for the access token.'
        )
        return self.repository.get_access_token()

    def get_expire(self) -> datetime:
        logger.info(
            'Bling Provider | Searching the Database for the access tokens'
            ' expiration.'
        )
        return self.repository.get_expire()

    def use_refresh_token(self) -> str:
        logger.info(
            'Bling Provider | Starting the refresh token usage flow.'
        )
        refresh_flow = oAuthRefreshBling(
            self.repository, self.adapter_refresh
        )
        access_token: str = refresh_flow.refresh_token_flow_bling()
        logger.info('Bling Provider | Refresh token flow completed.')
        return access_token
