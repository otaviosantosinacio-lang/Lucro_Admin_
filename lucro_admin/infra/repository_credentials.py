import logging
from datetime import datetime
from pathlib import Path

from dotenv import set_key

logger = logging.getLogger('lucroadmin.infra.repositorycredentials')


class SaveCredentials():
    def __init__(self, env_file: str):
        self.env_file = env_file

    def valid_env(self):
        env = Path(self.env_file)
        env_exist = env.exists()
        if env_exist:
            return env_exist
        else:
            root_dir = Path(__file__).resolve().parents[2]
            env_dir = root_dir / self.env_file
            env_dir.mkdir(exist_ok=True)
            return True

    def save_credentials(
        self,
        access_token: str,
        refresh_token: str,
        expire:  int | datetime
    ):

        logger.info(
            'Repository Credentials | '
            'Starting save a new credentials of external api.'
        )
        expire_str = str(expire)
        self.valid_env()
        set_key(self.env_file, 'ACCESS_TOKEN', access_token)
        set_key(self.env_file, 'REFRESH_TOKEN', refresh_token)
        set_key(self.env_file, 'EXPIRE', expire_str)

        logger.info(
            'Repository Credentials | '
            'Finished save a new credentials of external api.'
        )

        return True
