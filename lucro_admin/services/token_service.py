import logging
from datetime import datetime

logger = logging.getLogger('lucroadmin.services.bling')


class TokenService:

    def __init__(self, provider):
        self.provider = provider

    def validate_access_token(self) -> str:
        """
        validate_access_token -> Setting the validity of the access token if
        it is invalid, it immediately starts the flow to obtain a valid one

        :return: Valid Access Token
        :rtype: str
        """
        breakpoint()
        expire = self.provider.get_expire()
        expired: bool = datetime.now() >= expire
        if expired:
            logger.info(
                'Lucro Admin Token Service |'
                ' Token expired, starting refresh flow'
            )
            access_token: str = self.provider.use_refresh_token()
            return access_token
        else:
            logger.info('Lucro Admin Token Service | Valid token')
            access_token: str = self.provider.get_access_token()
            return access_token
