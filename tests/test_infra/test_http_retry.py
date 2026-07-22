from http import HTTPStatus

import requests

from lucro_admin.infra.http.retry import RetryPolicy
from tests.fakes.http import FakeResponse



def test_retrypolicy_success():
    def fake_get(url):
        return FakeResponse(
                status_code=HTTPStatus.OK
            )

    url = 'lucroadmin.com/home'

    retry = RetryPolicy()

    response = retry.execute(
        lambda: fake_get(url)
    )

    assert response.status_code == HTTPStatus.OK


def test_retrypolicy_rate_limited():
    def fake_get(url):
        return FakeResponse(
                status_code=HTTPStatus.TOO_MANY_REQUESTS
            )

    url = 'lucroadmin.com/home'

    retry = RetryPolicy()

    response = retry.execute(
        lambda: fake_get(url)
    )

    assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS


def test_retrypolicy_critical_erro():
    def fake_get(url):
        return FakeResponse(
                status_code=HTTPStatus.BAD_REQUEST
            )

    url = 'lucroadmin.com/home'

    retry = RetryPolicy()

    response = retry.execute(
        lambda: fake_get(url)
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
