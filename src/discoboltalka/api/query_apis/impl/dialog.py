from __future__ import annotations

import typing as t
import itertools

from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert

from ..abc import ABCDialogQueryAPI
from ...adapters import dialog_table, context_table


if t.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.engine import Result
    from sqlalchemy.dialects.postgresql import Insert

    insert = Insert


class DialogQueryAPI(ABCDialogQueryAPI):
    def __init__(
        self,
        session: AsyncSession,
        max_len: int = 1000,
    ) -> None:
        self._session = session
        self._max_len = max_len

    async def get_last_contexts(self, user_id: int) -> list[str]:
        result = await self._select_context_rows_by_dialog_id(id_=user_id)
        await self._session.commit()

        return list(
            itertools.chain.from_iterable(
                (row.user_request, row.bot_response)
                for row in result.fetchall()
            ),
        )

    async def add_context(
        self,
        user_id: int,
        user_request: str,
        bot_response: str,
    ) -> None:
        await self._insert_to_dialog_table_if_exist(id_=user_id)
        await self._insert_to_context_table(
            user_request=user_request,
            bot_response=bot_response,
            dialog_id=user_id,
        )
        await self._session.commit()

    async def _select_context_rows_by_dialog_id(self, id_: int) -> Result:
        sql = select(context_table).where(context_table.c.dialog_id == id_).limit(self._max_len)
        return await self._session.execute(sql)

    async def _insert_to_dialog_table_if_exist(
        self,
        id_: int,
    ) -> None:
        sql = insert(dialog_table).values(id=id_).on_conflict_do_nothing()
        await self._session.execute(sql)

    async def _insert_to_context_table(
        self,
        user_request: str,
        bot_response: str,
        dialog_id: int,
    ) -> None:
        sql = insert(context_table).values(
            user_request=user_request,
            bot_response=bot_response,
            dialog_id=dialog_id,
        )
        await self._session.execute(sql)
