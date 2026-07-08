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
