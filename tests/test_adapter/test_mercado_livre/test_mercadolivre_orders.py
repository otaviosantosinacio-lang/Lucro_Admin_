from http import HTTPStatus

import requests

from lucro_admin.adapters.mercado_livre.mercado_livre_orders import (
    GetMercadoLivre,
)
from tests.fakes.http import FakeResponse


def test_exchange_code_for_tokens_sucess(monkeypatch):
    def fake_get(url, headers, timeout):

        assert url == 'https://api.mercadolibre.com/orders'
        assert headers['Authorization'].startswith('Bearer ')
        assert headers['Accept'] == 'application/json'

        timeout_request = 20
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            text='200 -> Return EndPoint'
        )

    monkeypatch.setattr(requests, 'get', fake_get)

    client = GetMercadoLivre()
    url = 'https://api.mercadolibre.com/orders'
    result = client.get_endpoint(
        access_token='access_token_test_ml',
        url=url
        )

    assert result.status_code == HTTPStatus.OK
    assert result.text == '200 -> Return EndPoint'
