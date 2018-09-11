from typing import NamedTuple


class Message(NamedTuple):
    cls: str
    text: str
