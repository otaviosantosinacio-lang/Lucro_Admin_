from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any

import pytest

from lucro_admin.services.bling.credentials import (
    service_bling_credentials as service_module,
)
from lucro_admin.services.bling.credentials.service_bling_credentials import (
    oAuthCodeBling,
    oAuthRefreshBling,
)
from tests.fakes.repository import FakeRepository


class FakeRefreshAdapter:

    def __init__(self, response: dict[str, Any]):
        self.response = response

        self.received_credentials: (
            tuple[str, str, str] | None
        ) = None

    def refresh_access_token(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> dict[str, Any]:
        self.received_credentials = (
            client_id,
            client_secret,
            refresh_token,
        )

        return self.response


class FakeCodeAdapter:
    def __init__(self):
        self.generated_url_data: tuple[str, str] | None = None

        self.exchange_data: tuple[str, str, str] | None = None

    def generate_url_request(
        self,
        client_id: str,
        *,
        state: str,
    ) -> str:
        self.generated_url_data = (
            client_id,
            state,
        )

        return (
            "https://fake-bling.com/authorize"
            f"?client_id={client_id}&state={state}"
        )

    def exchange_code_for_tokens(
        self,
        client_id: str,
        client_secret: str,
        code: str,
    ) -> dict[str, Any]:
        self.exchange_data = (
            client_id,
            client_secret,
            code,
        )

        return {
            "fake": "response",
        }


@pytest.fixture
def repository() -> FakeRepository:

    return FakeRepository(
        access_token="old-access-token",
        refresh_token="old-refresh-token",
        client_id="client-id",
        client_secret="client-secret",
        expire=datetime(2026, 7, 22, 10, 0),
        salva_tokens=True,
    )


def create_fake_credential(
    status_code: HTTPStatus = HTTPStatus.OK,
) -> SimpleNamespace:

    return SimpleNamespace(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
        expire=datetime(2026, 7, 23, 10, 0),
        response_status_code=status_code,
    )


def test_refresh_flow_should_return_and_save_new_access_token(
    repository: FakeRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    credential = create_fake_credential()

    adapter = FakeRefreshAdapter(
        response={
            "fake": "response",
        }
    )

    monkeypatch.setattr(
        service_module.Credential,
        "from_api_response",
        lambda _response: credential,
    )

    service = oAuthRefreshBling(
        repository=repository,
        adapt_refresh=adapter,
    )

    result = service.refresh_token_flow_bling()

    assert result == "new-access-token"

    assert adapter.received_credentials == (
        "client-id",
        "client-secret",
        "old-refresh-token",
    )

    assert repository.saved_tokens == (
        "new-access-token",
        "new-refresh-token",
        datetime(2026, 7, 23, 10, 0),
    )

    assert repository.access_token == "new-access-token"
    assert repository.refresh_token == "new-refresh-token"


@pytest.mark.parametrize(
    "missing_field",
    [
        "client_id",
        "client_secret",
        "refresh_token",
    ],
)
def test_refresh_flow_should_raise_when_credentials_are_missing(
    missing_field: str,
    repository: FakeRepository,
) -> None:

    setattr(
        repository,
        missing_field,
        "",
    )

    adapter = FakeRefreshAdapter(
        response={},
    )

    service = oAuthRefreshBling(
        repository=repository,
        adapt_refresh=adapter,
    )

    with pytest.raises(
        Exception,
        match="Credentials not found",
    ):
        service.refresh_token_flow_bling()

    # O adapter não pode ser chamado sem credenciais.
    assert adapter.received_credentials is None

    # Nenhum token pode ser salvo.
    assert repository.saved_tokens is None


def test_refresh_flow_should_start_code_flow_when_refresh_fails(
    repository: FakeRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    credential = create_fake_credential(
        status_code=HTTPStatus.UNAUTHORIZED,
    )

    adapter = FakeRefreshAdapter(
        response={
            "error": "invalid_grant",
        }
    )

    monkeypatch.setattr(
        service_module.Credential,
        "from_api_response",
        lambda _response: credential,
    )

    received_repository: list[FakeRepository] = []

    class FakeOAuthCodeBling:
        def __init__(
            self,
            code_repository: FakeRepository,
        ):
            received_repository.append(
                code_repository,
            )

        def oAuthCode_flow_bling(self) -> str:
            return "access-token-from-code-flow"

    monkeypatch.setattr(
        service_module,
        "oAuthCodeBling",
        FakeOAuthCodeBling,
    )

    service = oAuthRefreshBling(
        repository=repository,
        adapt_refresh=adapter,
    )

    result = service.refresh_token_flow_bling()

    assert result == "access-token-from-code-flow"

    assert received_repository == [
        repository,
    ]

    assert repository.saved_tokens is None


def test_code_flow_should_save_and_return_access_token(
    repository: FakeRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    credential = create_fake_credential()

    code_adapter = FakeCodeAdapter()

    opened_urls: list[str] = []

    monkeypatch.setattr(
        service_module,
        "Code",
        lambda: code_adapter,
    )

    monkeypatch.setattr(
        service_module,
        "cript_state",
        lambda: "expected-state",
    )

    monkeypatch.setattr(
        service_module,
        "code_string",
        lambda: {
            "code": "authorization-code",
            "state": "expected-state",
        },
    )

    monkeypatch.setattr(
        service_module.webbrowser,
        "open",
        lambda url: opened_urls.append(url),
    )

    monkeypatch.setattr(
        service_module.Credential,
        "from_api_response",
        lambda _response: credential,
    )

    service = oAuthCodeBling(
        repository=repository,
    )

    result = service.oAuthCode_flow_bling()

    assert result == "new-access-token"

    assert code_adapter.generated_url_data == (
        "client-id",
        "expected-state",
    )

    assert opened_urls == [
        (
            "https://fake-bling.com/authorize"
            "?client_id=client-id&state=expected-state"
        )
    ]

    assert code_adapter.exchange_data == (
        "client-id",
        "client-secret",
        "authorization-code",
    )

    assert repository.saved_tokens == (
        "new-access-token",
        "new-refresh-token",
        datetime(2026, 7, 23, 10, 0),
    )


def test_code_flow_should_raise_when_state_is_invalid(
    repository: FakeRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    code_adapter = FakeCodeAdapter()

    monkeypatch.setattr(
        service_module,
        "Code",
        lambda: code_adapter,
    )

    monkeypatch.setattr(
        service_module,
        "cript_state",
        lambda: "expected-state",
    )

    monkeypatch.setattr(
        service_module,
        "code_string",
        lambda: {
            "code": "authorization-code",
            "state": "invalid-state",
        },
    )

    monkeypatch.setattr(
        service_module.webbrowser,
        "open",
        lambda _url: True,
    )

    service = oAuthCodeBling(
        repository=repository,
    )

    with pytest.raises(
        Exception,
        match="The returned state is not valid",
    ):
        service.oAuthCode_flow_bling()

    # Não pode trocar o code por tokens.
    assert code_adapter.exchange_data is None

    # Não pode salvar nenhuma credencial.
    assert repository.saved_tokens is None


def test_refresh_flow_should_return_token_when_save_fails(
    repository: FakeRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    repository.salva_tokens = False

    credential = create_fake_credential()

    adapter = FakeRefreshAdapter(
        response={
            "fake": "response",
        }
    )

    monkeypatch.setattr(
        service_module.Credential,
        "from_api_response",
        lambda _response: credential,
    )

    service = oAuthRefreshBling(
        repository=repository,
        adapt_refresh=adapter,
    )

    result = service.refresh_token_flow_bling()

    assert result == "new-access-token"

    assert repository.saved_tokens == (
        "new-access-token",
        "new-refresh-token",
        datetime(2026, 7, 23, 10, 0),
    )

    assert repository.access_token == "old-access-token"
    assert repository.refresh_token == "old-refresh-token"
