from http import HTTPStatus

import requests

from lucro_admin.adapters.bling.bling_orders import GetUrlXML, CrudBling
from tests.fakes.http import FakeResponse


def test_get_endpoint_sucess(monkeypatch):
    def fake_get(url, headers, timeout):

        assert url == 'https://api.bling.com.br/Api/v3'
        assert headers['Accept'] == 'application/json'
        assert headers['Authorization'].startswith('Bearer ')
        assert headers['enable-jwt'] == '1'

        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            text='200 -> Return EndPoint'
        )

    monkeypatch.setattr(requests, 'get', fake_get)

    client = CrudBling()
    url = 'https://api.bling.com.br/Api/v3'
    result = client.get_endpoint(
        access_token='access_token_test',
        url=url
        )

    assert result.status_code == HTTPStatus.OK
    assert result.text == '200 -> Return EndPoint'


def test_request_xml_endpoint_sucess(monkeypatch):
    def fake_get(url, timeout):

        assert url == 'https://api.bling.com.br/Api/v3/nfe'

        timeout_request = 30
        assert timeout == timeout_request

        return FakeResponse(
            status_code=HTTPStatus.OK,
            text='200 -> Return EndPointXML'
        )

    monkeypatch.setattr(requests, 'get', fake_get)

    client = GetUrlXML()
    url = 'https://api.bling.com.br/Api/v3/nfe'
    result = client.request_xml(
        url=url
        )

    assert result == '200 -> Return EndPointXML'
