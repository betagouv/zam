from typing import Iterator

from logbook import warn


def strip_styles(content: str) -> str:
    needle = ' style="text-align:justify;"'
    if needle in content:
        return content.replace(needle, '')
    return content


def warnumerate(items: list, limit: int) -> Iterator[dict]:
    for index, raw_article in enumerate(items):
        if limit and index >= limit:
            warn(f'Only {limit} items loaded.')
            break
        yield raw_article
