rom http from os import access

import HTTPStatus

import requests

from lucro_admin.adapters.mercado_livre.mercado_livre_orders import (
    GetMercadoLivre
)
from tests.fakes.http import FakeResponse


def test_exchange_code_for_tokens_sucess(monkeypatch):
    def fake_get(url, headers, timeout):

        assert url == 'https://api.mercadolibre.com/oauth/token'
        assert headers['Authorization'].startwith('Bearer ')
        assert headers['accept'] == 'application/json'

        timeout_request = 20
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            text='200 -> Return EndPoint'
        )

    monkeypatch.setattr(requests, 'get', fake_get)

    client = GetMercadoLivre()
    url = 'https://lucroadmin.com.br'
    result = client.get_endpoint(
        access_token='access_token_test_ml',
        url=url
        )

    expire_test = 3600

    assert result['response_status_code'] == HTTPStatus.OK
    assert result['access_token'] == 'access-token-test-ml'
    assert result['refresh_token'] == 'refresh-token-test-ml'
    assert result['expire'] == expire_test
