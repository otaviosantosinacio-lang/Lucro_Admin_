from abc import ABC, abstractmethod
from datetime import datetime


class TokenProvider(ABC):
    """
    Aqui definimos o contrato que todas as APIs devem fornecer para o token service
    """

    @abstractmethod
    def get_access_token(self) -> str:
        """Retorna o access token atual"""
        pass

    @abstractmethod
    def get_expire(self) -> datetime:
        """Retorna o datetime de expiração do token"""
        pass

    @abstractmethod
    def use_refresh_token(self) -> str:
        """Executa o fluxo de refresh token"""
        pass
