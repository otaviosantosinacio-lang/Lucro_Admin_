from datetime import datetime


class FakeRepository:
    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        expire: datetime,
        salva_tokens: bool = True,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.expire = expire

        # Define se o salvamento deve retornar sucesso ou falha.
        self.salva_tokens = salva_tokens

        # Guarda os tokens recebidos pelo método salva_token.
        self.saved_tokens: tuple[str, str, datetime] | None = None

    def get_access_token(self) -> str:
        return self.access_token

    def get_expire(self) -> datetime:
        return self.expire

    def get_refresh_token(self) -> str:
        return self.refresh_token

    def get_client_id(self) -> str:
        return self.client_id

    def get_client_secret(self) -> str:
        return self.client_secret

    def salva_token(
        self,
        access_token: str,
        refresh_token: str,
        expire: datetime,
    ) -> bool:
        self.saved_tokens = (
            access_token,
            refresh_token,
            expire,
        )

        if not self.salva_tokens:
            return False

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expire = expire

        return True
