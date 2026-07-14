from http import HTTPStatus

import requests

from lucro_admin.adapters.mercado_livre.mercado_livre_credentials import (
    Code,
    RefreshML,
)
from tests.fakes.http import FakeResponse


def test_exchange_code_for_tokens_sucess(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.mercadolibre.com/oauth/token'
        assert headers['content-type'] == 'application/x-www-form-urlencoded'
        assert headers['accept'] == 'application/json'

        assert data == {
            'grant_type': 'authorization_code',
            'client_id': 'client_id_test_ml',
            'client_secret': 'client_secret_test_ml',
            'code': 'code_test_ml',
            'redirect_uri': 'https://lucroadmin.com.br'
        }
        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            payload={
                'response_status_code': HTTPStatus.OK,
                'access_token': 'access-token-test-ml',
                'refresh_token': 'refresh-token-test-ml',
                'expires_in': 3600
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Code()
    url = 'https://lucroadmin.com.br'
    result = client.exchange_code_for_tokens(
        client_id='client_id_test_ml',
        client_secret='client_secret_test_ml',
        code='code_test_ml',
        redirect_url=url
        )

    expire_test = 3600

    assert result['response_status_code'] == HTTPStatus.OK
    assert result['access_token'] == 'access-token-test-ml'
    assert result['refresh_token'] == 'refresh-token-test-ml'
    assert result['expire'] == expire_test


def test_exchange_code_for_tokens_too_many_requests(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.mercadolibre.com/oauth/token'
        assert headers['content-type'] == 'application/x-www-form-urlencoded'
        assert headers['accept'] == 'application/json'

        assert data == {
            'grant_type': 'authorization_code',
            'client_id': 'client_id_test_ml',
            'client_secret': 'client_secret_test_ml',
            'code': 'code_test_ml',
            'redirect_uri': 'https://lucroadmin.com.br'
        }
        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            payload={
                'response_status_code': HTTPStatus.TOO_MANY_REQUESTS,
                'access_token': 'too-many-requests',
                'refresh_token': 'too-many-requests',
                'expires_in': 1
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Code()
    url = 'https://lucroadmin.com.br'
    result = client.exchange_code_for_tokens(
        client_id='client_id_test_ml',
        client_secret='client_secret_test_ml',
        code='code_test_ml',
        redirect_url=url
        )

    expire_test = 100

    assert result['response_status_code'] == HTTPStatus.TOO_MANY_REQUESTS
    assert result['access_token'] is None
    assert result['refresh_token'] is None
    assert result['expire'] == expire_test


def test_exchange_code_for_tokens_critical_error(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.mercadolibre.com/oauth/token'
        assert headers['content-type'] == 'application/x-www-form-urlencoded'
        assert headers['accept'] == 'application/json'

        assert data == {
            'grant_type': 'authorization_code',
            'client_id': 'client_id_test_ml',
            'client_secret': 'client_secret_test_ml',
            'code': 'code_test_ml',
            'redirect_uri': 'https://lucroadmin.com.br'
        }
        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            payload={
                'response_status_code': HTTPStatus.BAD_REQUEST,
                'access_token': 'bad-request',
                'refresh_token': 'bad-request',
                'expires_in': 1
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Code()
    url = 'https://lucroadmin.com.br'
    result = client.exchange_code_for_tokens(
        client_id='client_id_test_ml',
        client_secret='client_secret_test_ml',
        code='code_test_ml',
        redirect_url=url
        )

    expire_test = 100

    assert result['response_status_code'] == HTTPStatus.BAD_REQUEST
    assert result['access_token'] is None
    assert result['refresh_token'] is None
    assert result['expire'] == expire_test


def test_using_refresh_token_sucess(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.mercadolibre.com/oauth/token'
        assert headers['accept'] == 'application/json'
        assert headers['content-type'] == 'application/x-www-form-urlencoded'

        assert data == {
            'grant_type': 'refresh_token',
            'client_id': 'client_id_test_ml',
            'client_secret': 'client_secret_test_ml',
            'refresh_token': 'refresh_test_ml'
        }
        timeout_request = 20
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            payload={
                'response_status_code': HTTPStatus.OK,
                'access_token': 'access-token-test-ml',
                'refresh_token': 'refresh-token-test-ml',
                'expires_in': 3600
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = RefreshML()
    result = client.using_refresh_token(
        client_id='client_id_test_ml',
        client_secret='client_secret_test_ml',
        refresh_token='refresh_test_ml'
        )

    expire_test = 3600

    assert result['response_status_code'] == HTTPStatus.OK
    assert result['access_token'] == 'access-token-test-ml'
    assert result['refresh_token'] == 'refresh-token-test-ml'
    assert result['expire'] == expire_test
