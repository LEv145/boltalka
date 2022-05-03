from __future__ import annotations

import re
import logging
import textwrap
from datetime import datetime

import hikari

from .modules.boltalka_api import (
    BoltalkaAPI,
    ValidationError,
    ClientResponseError,
)
from .used_objects import ErrorEmbed
from .abstract_repositories import AbstractDialogRepository


_logger = logging.getLogger(__name__)


class BoltalkaEvents():
    def __init__(
        self,
        boltalka_api: BoltalkaAPI,
        dialog_repository: AbstractDialogRepository,
        channels_for_conversation: list | None = None,
    ) -> None:
        self._boltalka_api = boltalka_api
        self._dialog_repository = dialog_repository
        self._channels_for_conversation = channels_for_conversation

    async def on_guild_message_create(self, event: hikari.GuildMessageCreateEvent) -> None:
        if not isinstance(event.app, hikari.GatewayBot):
            raise RuntimeError("App should be 'hikari.GatewayBot'")


        if (
            event.is_bot
            or event.message.content is None
            # Favorable conditions
            or (
                # If client wasn't pinged
                event.app.cache.get_me().id not in event.message.mentions.users
                and (
                    self._channels_for_conversation is not None
                    and int(event.message.channel_id) not in self._channels_for_conversation
                )
            )
        ):
            return


        # Prepare content
        user_request = await self._clean_content_from_guild_message_create_event(
            event=event,
            content=event.message.content,
        )
        if not user_request:
            return

        last_context = await self._dialog_repository.get_last_contexts()
        context = last_context + [user_request]

        _logger.debug(f"Boltalka context: {context}")

        try:
            async with event.app.rest.trigger_typing(event.message.channel_id):
                boltalka_phrases = await self._boltalka_api.predict([context])
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

        bot_response = boltalka_phrases[0]
        _logger.info(f"Boltalka response: {user_request!r} -> {bot_response!r}")

        await self._dialog_repository.add_context(
            user_request,
            bot_response,
        )

        clean_boltalka_phrase = textwrap.shorten(bot_response, width=2000)

        await event.message.respond(
            clean_boltalka_phrase,
            reply=True,
            mentions_reply=True,
            mentions_everyone=False,
            role_mentions=False,
            user_mentions=False,
        )

    async def _clean_content_from_guild_message_create_event(
        self,
        event: hikari.GuildMessageCreateEvent,
        content: str,
    ) -> str:
        guild = event.get_guild()  # TODO: Check
        clean_content = content
        app = event.app

        if not isinstance(app, hikari.GatewayBot):
            raise RuntimeError("App should be 'hikari.GatewayBot'")

        def member_repl(match: re.Match) -> str:
            user_id = match[1]

            if user_id == str(app.cache.get_me().id):
                return ""

            member = guild.get_member(user=user_id)
            if member is not None:
                return f"@{member.display_name}"
            return ""

        def role_repl(match: re.Match) -> str:
            role_id = match[1]

            role = guild.get_role(role=role_id)
            if role is not None:
                return f"@{role.name}"
            return ""

        def channel_repl(match: re.Match) -> str:
            channel_id = match[1]

            channel = guild.get_channel(channel=channel_id)
            if channel is not None:
                return f"#{channel.name}"
            return ""

        def timestamp_repl(match: re.Match) -> str:
            timestamp_ = match[1]
            return str(datetime.fromtimestamp(timestamp_))

        clean_content = clean_content.replace("\n", " ")

        clean_content = re.sub(r'<@&([1-9]\d+)>', role_repl, clean_content)
        clean_content = re.sub(r'<#([1-9]\d+)>', channel_repl, clean_content)
        clean_content = re.sub(r'<@!?([1-9]\d+)>', member_repl, clean_content)
        clean_content = re.sub(r'<t:(\d)+(?::[a-zA-Z])?>', timestamp_repl, clean_content)
        clean_content = re.sub(r'<a?:[^:]+:[1-9]\d+>', "", clean_content)

        # Markdown
        # clean_content = re.sub(r'(?:[^\\]|^)\*\*\*([^*]+)\*\*\*', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)\*\*([^*]+)\*\*', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)\*([^*]+)\*', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)(?:[a-z]+\s)?```([^`]+)```', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)`([^`]+)`', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)__([^_]+)__', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)~~([^~]+)~~', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)\|\|([^|]+)\|\|', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)>>>\ ([^>]+)', r'\1', clean_content)
        # clean_content = re.sub(r'(?:[^\\]|^)>\ ([^>]+)$', r'\1', clean_content)

        clean_content = clean_content.strip()

        return clean_content
