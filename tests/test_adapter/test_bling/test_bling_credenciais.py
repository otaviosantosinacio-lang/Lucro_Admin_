from email.policy import HTTP
from http import HTTPStatus

import requests

from lucro_admin.adapters.bling.bling_credenciais import Code


class FakeResponse:
    def __init__(
        self,
        status_code: int,
        payload: dict | None = None,
        text: str = ""
):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_exchange_code_for_tokens(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.bling.com.br/Api/v3/oauth/token'
        assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
        assert headers['Accept'] == 'application/json'
        assert headers['Authorization'].startswith('Basic ')
        assert headers['enable-jwt'] == '1'

        assert data == {
                'grant_type': 'authorization_code',
            'code': 'code-test'
        }

        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            payload={
                'access_token': 'access-token-test',
                'refresh_token': 'refresh-token-test',
                'expires_in': 3600,
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Code()

    result = client.exchange_code_for_tokens(
        client_id='client_id_test',
        client_secret='client_secret_test',
        code='code-test'
        )

    assert result["access_token"] == "access-token-test"
    assert result["refresh_token"] == "refresh-token-test"

