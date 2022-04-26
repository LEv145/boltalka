from __future__ import annotations

import re
import logging
import textwrap
import typing as t
from datetime import datetime

import hikari

from .boltalka_api import (
    BoltalkaAPI,
    ValidationError,
    ClientResponseError,
)
from .used_objects import ErrorEmbed


_logger = logging.getLogger("discoboltalka.boltalka_gateway_bot")


# noinspection PyAbstractClass
class BoltalkaGatewayBot(hikari.GatewayBot):
    def __init__(self, boltalka_api: BoltalkaAPI, token: str, **kwargs: t.Any) -> None:
        super().__init__(token, **kwargs)
        self._boltalka_api = boltalka_api
        self.subscribe_listens()

    def subscribe_listens(self):
        self.subscribe(hikari.GuildMessageCreateEvent, self.message_listen)

    async def message_listen(self, event: hikari.GuildMessageCreateEvent) -> None:
        rest_client = event.app.rest

        content = event.message.content
        if event.is_bot or event.content is None:
            return

        # If client was pinged
        if self.cache.get_me().id not in event.message.mentions.users:
            return

        # Prepare content
        clean_content = await self._get_clean_content_from_guild_message_create_event(
            event=event,
            content=content,
        )
        if not clean_content:
            return

        try:
            async with rest_client.trigger_typing(event.message.channel_id):
                boltalka_phrases = await self._boltalka_api.predict([[clean_content]])
        except ValidationError:
            await event.message.respond(
                embed=ErrorEmbed("Я не смогла понять ваш текст"),
            )
            return
        except ClientResponseError:
            await event.message.respond(
                embed=ErrorEmbed("Мои сервера дали сбой, спросите позже"),
            )
            return

        boltalka_phrase = boltalka_phrases[0]

        _logger.info(f"Boltalka response: {content!r} -> {boltalka_phrase!r}")

        clean_boltalka_phrase = textwrap.shorten(boltalka_phrase, width=2000)

        await event.message.respond(
            clean_boltalka_phrase,
            reply=True,
            mentions_reply=True,
            mentions_everyone=False,
            role_mentions=False,
            user_mentions=False,
        )

    async def _get_clean_content_from_guild_message_create_event(
        self,
        event: hikari.GuildMessageCreateEvent,
        content: str,
    ) -> str:
        guild = event.get_guild()
        clean_content = content

        def member_repl(match: re.Match) -> str:
            user_id = match[0]

            member = guild.get_member(user=user_id)
            if member is not None:
                return f"@{member.display_name}"
            return ""

        def role_repl(match: re.Match) -> str:
            role_id = match[0]

            role = guild.get_role(role=role_id)
            if role is not None:
                return f"@{role.name}"
            return ""

        def channel_repl(match: re.Match) -> str:
            channel_id = match[0]

            channel = guild.get_channel(channel=channel_id)
            if channel is not None:
                return f"#{channel.name}"
            return ""

        def timestamp_repl(match: re.Match) -> str:
            timestamp_ = match[0]
            return str(datetime.fromtimestamp(timestamp_))

        def discord_emoji_repl(_match: re.Match) -> str:
            return ""

        clean_content = re.sub(r'<@&(\d[1-9]+)>', role_repl, clean_content)
        clean_content = re.sub(r'<#(\d[1-9]+)>', channel_repl, clean_content)
        clean_content = re.sub(r'<@!?(\d[1-9]+)>', member_repl, clean_content)
        clean_content = re.sub(r'<t:(\d)+(?::[a-zA-Z])?>', timestamp_repl, clean_content)
        clean_content = re.sub(r'<a?:[^:]+:\d[1-9]+>', discord_emoji_repl, clean_content)

        return clean_content.lstrip()
