import abc


class AbstractDialogRepository(abc.ABC):
    @abc.abstractmethod
    async def get_last_contexts(self, user_id: int) -> list[str]:
        pass

    @abc.abstractmethod
    async def add_context(
        self,
        user_id: int,
        user_request: str,
        bot_response: str,
    ) -> None:
        pass
