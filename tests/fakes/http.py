from typing import Any


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

    def json(self) -> dict[str, Any]:
        return self._payload
