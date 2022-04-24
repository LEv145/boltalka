from __future__ import annotations

import logging
import typing as t

import hikari

from discoboltalka.boltalka_api import (
    BoltalkaAPI,
    ValidationError,
)


_logger = logging.getLogger("discoboltalka.boltalka_gateway_bot")


# noinspection PyAbstractClass
class BoltalkaGatewayBot(hikari.GatewayBot):
    def __init__(self, boltalka_api: BoltalkaAPI, token: str, **kwargs: t.Any) -> None:
        super().__init__(token, **kwargs)
        self._boltalka_api = boltalka_api
        self.subscribe_listens()

    def subscribe_listens(self):
        self.subscribe(hikari.MessageCreateEvent, self.message_listen)

    async def message_listen(self, event: hikari.MessageCreateEvent) -> None:
        content = event.content
        if event.is_bot or event.content is None:
            return

        # noinspection PyUnresolvedReferences
        client_id = event.app.cache.get_me().id
        client_mention_string = f"<@{client_id}>"

        if client_mention_string not in content:
            return

        content = content.replace(client_mention_string, "").lstrip()

        try:
            boltalka_phrases = await self._boltalka_api.predict([[content]])
        except ValidationError:
            await event.message.respond(
                embed=hikari.Embed(
                    title="Ошибка",
                    description="Я не смогла понять ваш текст",
                    colour=0xbd0505,
                )
            )  # TODO?: Error handler or error embed
            return

        boltalka_phrase = boltalka_phrases[0]

        _logger.info(f"Boltalka response: {content!r} -> {boltalka_phrase!r}")

        await event.message.respond(boltalka_phrases[0])
