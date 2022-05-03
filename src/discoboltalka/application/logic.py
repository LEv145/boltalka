import asyncio
from pathlib import Path

import aiohttp
import hikari

from discoboltalka.api import (
    BoltalkaAPI,
    BoltalkaEvents,
    DialogRepository,
)

from .config import TomlConfigLoader


async def async_main() -> None:
    config_loader = TomlConfigLoader(Path("config.toml"))
    config = config_loader.load()

    client_session = aiohttp.ClientSession()
    boltalka_api = BoltalkaAPI(
        client_session=client_session,
        client_name=config.boltalka_config.client_name,
    )
    boltalka_event = BoltalkaEvents(
        boltalka_api=boltalka_api,
        dialog_repository=DialogRepository(),
        channels_for_conversation=config.message_event_config.channels_for_conversation,
    )

    bot = hikari.GatewayBot(
        token=config.bot_config.token,
        intents=hikari.Intents.GUILD_MESSAGES | hikari.Intents.GUILDS,
    )
    bot.subscribe(
        hikari.GuildMessageCreateEvent,
        boltalka_event.on_guild_message_create,
    )

    try:
        await bot.start()
        await bot.join()
    finally:
        await bot.close()
        await client_session.close()


def main() -> None:
    asyncio.run(async_main())

