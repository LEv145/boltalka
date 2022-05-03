from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MainConfig():
    bot_config: BotConfig
    boltalka_config: BoltalkaConfig
    message_event_config: MessageEventConfig


@dataclass
class BotConfig():
    token: str


@dataclass
class BoltalkaConfig():
    client_name: str


@dataclass
class MessageEventConfig():
    channels_for_conversation: list | None
