import typing as t
import abc


class AbstractDialogRepository(abc.ABC):
    @abc.abstractmethod
    async def get_last_contexts(self) -> t.List[str]:
        pass

    @abc.abstractmethod
    async def add_context(
        self,
        user_request: str,
        bot_response: str,
    ) -> None:
        pass
