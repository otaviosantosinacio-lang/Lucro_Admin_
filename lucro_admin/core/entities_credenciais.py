import logging
from dataclasses import dataclass
from datetime import datetime

from lucro_admin.utils.time import somandosecs

logger = logging.getLogger('lucroadmin.core.entities')


@dataclass
class Credencial:
    """
    Credencial

    Attributes:
        access_token: Token de acesso atual (Bearer)
        refresh_token: Token com expiração maior para obter o próximo
        access token quando expirado
        expire: Data/hora/segundos de quando o access token expira
        response_status_code: Status HTTP para controle de erros
    """

    access_token: str
    refresh_token: str
    expire: datetime
    response_status_code: int

    @classmethod
    def from_api_response(cls, response_data: dict) -> 'Credencial':
        """Converte retorno da API (com expire em segundos) para Credenciais"""
        return cls(
            access_token=response_data['access_token'],
            refresh_token=response_data['refresh_token'],
            expire=somandosecs(
                response_data['expire']
            ),  # Converte int para datetime
            response_status_code=response_data['response_status_code'],
        )
