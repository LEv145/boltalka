from __future__ import annotations

import re
import json as _json
import typing as t


if t.TYPE_CHECKING:
    from aiohttp import ClientSession


class BoltalkaAPI():
    def __init__(
        self,
        client_session: ClientSession,
        client_name: str = "Bot",
        json_loader: t.Callable[[str], t.Any] = _json.loads,
    ) -> None:
        self._json_loader = json_loader
        self._client_session = client_session
        self._client_name = client_name

    async def predict(self, contexts: t.List[t.List[str]]) -> t.List[str]:
        """
        Exceptions:
            ValidationError
        """
        json_response = await self._request(
            url="https://api.aicloud.sbercloud.ru/public/v2/boltalka/predict",
            json=dict(instances=[dict(contexts=contexts)]),
        )

        responses = re.findall("'([^']+)'", json_response["responses"])

        return [
            context.replace("%bot_name", self._client_name)  # TODO?: Template
            for context in responses
        ]

    async def _request(self, url: str, json: t.Any) -> t.Any:
        """
        Exceptions:
            ValidationError
        """
        async with self._client_session.post(
            url=url,
            json=json,
        ) as response:
            json_response = self._json_loader(await response.text())

        detail = json_response.get("detail")
        if detail is not None:
            raise ValidationError(
                message=detail[0]["msg"],
                location=detail[0]["loc"],
                type_=detail[0]["type"],
            )

        return json_response


class APIError(Exception):
    ...


class ValidationError(APIError):
    def __init__(
        self,
        message: str,
        location: t.List[t.Any],
        type_: str,
    ) -> None:
        self.message = message
        self.location = location
        self.type_ = type_
