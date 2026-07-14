from http import HTTPStatus

import requests

from lucro_admin.adapters.bling.bling_credentials import Code, Refresh
from tests.fakes.http import FakeResponse


def test_exchange_code_for_tokens_sucess(monkeypatch):
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
    expire_test = 3600

    assert result['response_status_code'] == HTTPStatus.OK
    assert result['access_token'] == 'access-token-test'
    assert result['refresh_token'] == 'refresh-token-test'
    assert result['expire'] == expire_test


def test_exchange_code_for_tokens_too_many_requests(monkeypatch):
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
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            payload={
                'access_token': 'TOO_MANY_REQUESTS',
                'refresh_token': 'TOO_MANY_REQUESTS',
                'expires_in': 1,
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Code()

    result = client.exchange_code_for_tokens(
        client_id='client_id_test',
        client_secret='client_secret_test',
        code='code-test'
        )

    assert result['response_status_code'] == HTTPStatus.TOO_MANY_REQUESTS
    assert result['access_token'] is None
    assert result['refresh_token'] is None
    assert result['expire'] == 1


def test_exchange_code_for_tokens_critical_error(monkeypatch):
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
            status_code=HTTPStatus.BAD_REQUEST,
            payload={
                'access_token': 'BAD_REQUEST',
                'refresh_token': 'BAD_REQUEST',
                'expires_in': 1,
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Code()

    result = client.exchange_code_for_tokens(
        client_id='client_id_test',
        client_secret='client_secret_test',
        code='code-test'
        )

    assert result['response_status_code'] == HTTPStatus.BAD_REQUEST
    assert result['access_token'] is None
    assert result['refresh_token'] is None
    assert result['expire'] == 1


def test_generate_url_request():
    client = Code()

    client_id = 'client_id_test'
    state = 'state_test'
    result = client.generate_url_request(
                client_id=client_id,
                state=state
            )

    assert result == (
        'https://api.bling.com.br/Api/v3/oauth/authorize?response_type=code&'
        f'client_id={client_id}&state={state}'
    )


def test_refresh_access_token_sucess(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.bling.com.br/Api/v3/oauth/token'
        assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
        assert headers['Accept'] == 'application/json'
        assert headers['Authorization'].startswith('Basic ')
        assert headers['enable-jwt'] == '1'

        assert data == {
                'grant_type': 'refresh_token',
                'refresh_token': 'refresh-test'
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

    client = Refresh()

    result = client.refresh_access_token(
        client_id='client_id_test',
        client_secret='client_secret_test',
        refresh_token='refresh-test'
        )
    expire_test = 3600

    assert result['response_status_code'] == HTTPStatus.OK
    assert result['access_token'] == 'access-token-test'
    assert result['refresh_token'] == 'refresh-token-test'
    assert result['expire'] == expire_test


def test_refresh_access_token_too_many_requests(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.bling.com.br/Api/v3/oauth/token'
        assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
        assert headers['Accept'] == 'application/json'
        assert headers['Authorization'].startswith('Basic ')
        assert headers['enable-jwt'] == '1'

        assert data == {
                'grant_type': 'refresh_token',
                'refresh_token': 'refresh-test'
                }

        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            payload={
                'access_token': 'TOO_MANY_REQUESTS',
                'refresh_token': 'TOO_MANY_REQUESTS',
                'expires_in': 1,
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Refresh()

    result = client.refresh_access_token(
        client_id='client_id_test',
        client_secret='client_secret_test',
        refresh_token='refresh-test'
        )

    assert result['response_status_code'] == HTTPStatus.TOO_MANY_REQUESTS
    assert result['access_token'] is None
    assert result['refresh_token'] is None
    assert result['expire'] == 1


def test_refresh_access_token_critical_error(monkeypatch):
    def fake_post(url, headers, data, timeout):

        assert url == 'https://api.bling.com.br/Api/v3/oauth/token'
        assert headers['Content-Type'] == 'application/x-www-form-urlencoded'
        assert headers['Accept'] == 'application/json'
        assert headers['Authorization'].startswith('Basic ')
        assert headers['enable-jwt'] == '1'

        assert data == {
                'grant_type': 'refresh_token',
                'refresh_token': 'refresh-test'
                }

        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            payload={
                'access_token': 'BAD_REQUEST',
                'refresh_token': 'BAD_REQUEST',
                'expires_in': 1,
            }
        )

    monkeypatch.setattr(requests, 'post', fake_post)

    client = Refresh()

    result = client.refresh_access_token(
        client_id='client_id_test',
        client_secret='client_secret_test',
        refresh_token='refresh-test'
        )

    assert result['response_status_code'] == HTTPStatus.BAD_REQUEST
    assert result['access_token'] is None
    assert result['refresh_token'] is None
    assert result['expire'] == 1
