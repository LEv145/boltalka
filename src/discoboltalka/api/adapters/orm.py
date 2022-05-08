from sqlalchemy import (
    Table,
    MetaData,
    Column,
    BigInteger,
    String,
    ForeignKey,
)


sqlalchemy_metadata = MetaData()


dialog_table = Table(
    "dialog",
    sqlalchemy_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
)

context_table = Table(
    "context",
    sqlalchemy_metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("user_request", String),
    Column("bot_response", String),
    Column("dialog_id", ForeignKey("dialog.id")),
)
