from datetime import UTC, datetime
from http import HTTPStatus

import pytest
from freezegun import freeze_time

from lucro_admin.core.entities_credential import Credential


def test_entitiy_credential():
    with freeze_time('2025-04-01 13:00:00'):
        expire_test = 60
        credentials_dict: dict[str,str|int] = {
            'access_token': 'access_token_test',
            'refresh_token': 'refresh_token_test',
            'expire': expire_test,
            'response_status_code': HTTPStatus.OK
        }

        credentials: Credential = Credential.from_api_response(credentials_dict)
        expected_expiration = datetime(
            2025,
            4,
            1,
            13,
            1,
            tzinfo=UTC
        )
        assert credentials.access_token == 'access_token_test'
        assert credentials.refresh_token == 'refresh_token_test'
        assert credentials.expire == expected_expiration
        assert credentials.response_status_code == HTTPStatus.OK


def test_entitie_credential_without_access_token():
    expire_test = 60
    credentials_dict: dict[str,str|int] = {
        'refresh_token': 'refresh_token_test',
        'expire': expire_test,
        'response_status_code': HTTPStatus.OK
    }

    with pytest.raises(KeyError, match='access_token'):
        credentials: Credential = Credential.from_api_response(
            credentials_dict
            )
