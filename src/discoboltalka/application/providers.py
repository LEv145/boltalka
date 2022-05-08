from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

from discoboltalka.api import sqlalchemy_metadata

from .config import (
    PostgresConfig,
)


async def provide_postgres_session(config: PostgresConfig) -> AsyncSession:
    postgres_host, postgres_port = config.host.split(":")
    postgres_engine = create_async_engine(
        URL(
            drivername="postgresql+asyncpg",
            username=config.user,
            password=config.password,
            database=config.database_name,
            host=postgres_host,
            port=postgres_port,
        ),
    )
    async with postgres_engine.begin() as connect:
        await connect.run_sync(sqlalchemy_metadata.create_all)
    return sessionmaker(bind=postgres_engine, class_=AsyncSession)()

