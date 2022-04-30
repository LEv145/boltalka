from collections import deque
import typing as t
import asyncio

from ..abstract_repositories import AbstractDialogRepository


class DialogRepository(AbstractDialogRepository):
    def __init__(self, max_len: int = 1000) -> None:
        self._contexts = deque(maxlen=max_len * 2)  # Context = user_request + bot_response
        self._lock = asyncio.Lock()

    async def get_last_contexts(self) -> t.List[str]:
        return list(self._contexts)

    async def add_context(
        self,
        user_request: str,
        bot_response: str,
    ) -> None:
        async with self._lock:
            self._contexts.append(user_request)
            self._contexts.append(bot_response)
