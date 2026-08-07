import logging
from datetime import datetime

from dotenv import set_key

logger = logging.getLogger('lucroadmin.infra.repositorycredentials')


class SaveCredentials():
    def __init__(self, env_file: str):
        self.env_file = env_file

    def save_credentials(
        self,
        access_token: str,
        refresh_token: str,
        expire: datetime
    ):

        logger.info(
            'Repository Credentials | '
            'Starting save a new credentials of external api.'
        )
        expire_str = str(expire)

        set_key(self.env_file, 'ACCESS_TOKEN', access_token)
        set_key(self.env_file, 'REFRESH_TOKEN', refresh_token)
        set_key(self.env_file, 'EXPIRE', expire_str)

        logger.info(
            'Repository Credentials | '
            'Finished save a new credentials of external api.'
        )
