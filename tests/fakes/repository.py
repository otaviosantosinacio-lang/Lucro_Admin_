from datetime import datetime


class FakeRepository:
    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        expire: datetime,
        salva_tokens: bool
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.expire = expire
        self.save_token = salva_tokens

    def get_access_token(self):
        return self.access_token

    def get_expire(self):
        return self.expire

    def get_refresh_token(self):
        return self.refresh_token

    def get_client_id(self):
        return self.client_id

    def get_client_secret(self):
        return self.client_secret
