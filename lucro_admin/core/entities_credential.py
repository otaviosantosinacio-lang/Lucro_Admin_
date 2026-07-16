import logging
from dataclasses import dataclass
from datetime import datetime

from lucro_admin.utils.time import somandosecs

logger = logging.getLogger('lucroadmin.core.entities')


@dataclass
class Credential:
    """
    Credential

    Attributes:
        access_token: Current access token (Bearer)
        refresh_token: Token with a loger expiration
        expire: Date/time/seconds of when the access token expires
        response_status_code: HTTP status for error handling
    """

    access_token: str
    refresh_token: str
    expire: int | datetime
    response_status_code: int

    @classmethod
    def from_api_response(cls, response_data: dict) -> 'Credential':
        """
        access_tConverts API return (with expiry in seconds) to Credentials
        """
        return cls(
            access_token=response_data['access_token'],
            refresh_token=response_data['refresh_token'],
            expire=somandosecs(
                response_data['expire']
            ),  # Convert int for datetime
            response_status_code=response_data['response_status_code'],
        )
