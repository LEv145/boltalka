from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MainConfig():
    bot_config: BotConfig
    boltalka_config: BoltalkaConfig


@dataclass
class BotConfig():
    token: str
    channels_for_conversation: list | None


@dataclass
class BoltalkaConfig():
    client_name: str

