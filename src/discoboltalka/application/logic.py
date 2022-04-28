import asyncio
from pathlib import Path

import aiohttp
import hikari

from .config import TomlConfigLoader
from discoboltalka.api.boltalka_api import BoltalkaAPI
from discoboltalka.api.boltalka_gateway_bot import BoltalkaGatewayBot


async def async_main() -> None:
    config_loader = TomlConfigLoader(Path("config.toml"))
    config = config_loader.load()

    client_session = aiohttp.ClientSession()
    boltalka_api = BoltalkaAPI(
        client_session=client_session,
        client_name=config.boltalka_config.client_name,
    )

    bot = BoltalkaGatewayBot(
        token=config.bot_config.token,
        boltalka_api=boltalka_api,
        intents=hikari.Intents.GUILD_MESSAGES | hikari.Intents.GUILDS,
    )

    try:
        await bot.start()
        await bot.join()
    finally:
        await bot.close()
        await client_session.close()


def main() -> None:
    asyncio.run(async_main())

