from unittest import IsolatedAsyncioTestCase

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, insert

from discoboltalka.api.adapters.orm import sqlalchemy_metadata
from discoboltalka.api.repositories.dialog_repository import (
    context_table,
    dialog_table,
    DialogRepository,
)


class TestDialogRepository(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        engine = create_async_engine(
            "postgresql+asyncpg://discoboltalka_user:xxVcdmcR3AUB@127.0.0.1:5433/discoboltalka",
        )

        async with engine.begin() as connect:
            await connect.run_sync(sqlalchemy_metadata.drop_all)
            await connect.run_sync(sqlalchemy_metadata.create_all)

        self._session: AsyncSession = sessionmaker(bind=engine, class_=AsyncSession)()
        self._repository = DialogRepository(session=self._session, max_len=5)

    async def asyncTearDown(self) -> None:
        await self._session.close()

    async def test_get_last_contexts_without_dialog(self) -> None:
        user_id = 501089151089770517

        result = await self._repository.get_last_contexts(user_id)
        self.assertEqual(result, [])


    async def test_get_last_contexts_without_context(self) -> None:
        user_id = 501089151089770517

        await self._session.execute(insert(dialog_table).values(id=user_id))

        result = await self._repository.get_last_contexts(user_id)
        self.assertEqual(result, [])

    async def test_get_last_contexts_with_context(self) -> None:
        user_id = 501089151089770517

        await self._session.execute(insert(dialog_table).values(id=user_id))

        await self._session.execute(
            insert(context_table).values(
                user_request="Test11",
                bot_response="Test12",
                dialog_id=user_id,
            ),
        )
        await self._session.execute(
            insert(context_table).values(
                user_request="Test13",
                bot_response="Test14",
                dialog_id=user_id,
            ),
        )

        result = await self._repository.get_last_contexts(user_id)
        self.assertEqual(result, ["Test11", "Test12", "Test13", "Test14"])

    async def test_add_context(self) -> None:
        user_id = 501089151089770517

        await self._repository.add_context(
            user_id=user_id,
            user_request="Test1",
            bot_response="Test2",
        )
        await self._repository.add_context(
            user_id=user_id,
            user_request="Test3",
            bot_response="Test4",
        )

        result = await self._session.execute(
            select(context_table, dialog_table).join_from(context_table, dialog_table),
        )

        self.assertEqual(
            result.mappings().fetchall(),
            [
                dict(
                    id=1,
                    user_request="Test1",
                    bot_response="Test2",
                    dialog_id=user_id,
                    id_1=user_id,
                ),
                dict(
                    id=2,
                    user_request="Test3",
                    bot_response="Test4",
                    dialog_id=user_id,
                    id_1=user_id,
                ),
            ]
        )
