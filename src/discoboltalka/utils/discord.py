import re


def clean_content(content: str) -> str:
    content = re.sub(
        pattern=r"""
            <(?:@[!&]?|\#)[1-9][0-9]+> |  # Mentions (Member, channel, role)
            @here|@everyone |  # Here, everyone mentions
            <a?:[^:]+:[1-9][0-9]+> |  # Emojis
            <t:\d+(?::[a-zA-Z])?> |  # Time
            [_\\~|\*`]|^>(?:>>)?\s|\[.+\]\(.+\)  # Markdown
        """,
        repl="",
        string=content,
        flags=re.MULTILINE | re.VERBOSE,
    )
    return content
