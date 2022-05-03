from __future__ import annotations

import typing as t
import abc

from .models import (
    MainConfig,
    BotConfig,
    BoltalkaConfig,
    MessageEventConfig,
)

import toml


if t.TYPE_CHECKING:
    from pathlib import Path


class ABCLoader(abc.ABC):
    def load(self) -> MainConfig:
        """Load config and get config object."""


class TomlConfigLoader(ABCLoader):
    def __init__(self, path: Path):
        self._path = path

    def load(self) -> MainConfig:
        with open(self._path) as fp:
            config_raw_data = toml.load(fp)

        try:
            bot_raw_config = config_raw_data["bot"]
            bot_config = BotConfig(
                token=bot_raw_config["token"],
            )
        except KeyError as exception:
            raise InvalidConfig() from exception

        try:
            boltalka_raw_config = config_raw_data["boltalka"]
            boltalka_config = BoltalkaConfig(
                client_name=boltalka_raw_config["client_name"],
            )
        except KeyError as exception:
            raise InvalidConfig() from exception

        try:
            message_event_raw_config = config_raw_data["message_event"]
            message_event_config = MessageEventConfig(
                channels_for_conversation=message_event_raw_config.get("channels_for_conversation"),
            )
        except KeyError as exception:
            raise InvalidConfig() from exception


        return MainConfig(
            bot_config=bot_config,
            boltalka_config=boltalka_config,
            message_event_config=message_event_config,
        )


class InvalidConfig(Exception):
    """If config is invalid."""
