import hikari


class ErrorEmbed(hikari.Embed):
    def __init__(self, message: str) -> None:
        super().__init__(
            title="Ошибка",
            description=message,
            colour=0xbd0505,
        )
