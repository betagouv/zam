import sys


def strip_styles(content: str) -> str:
    needle = ' style="text-align:justify;"'
    if needle in content:
        return content.replace(needle, '')
    return content


def positive_hash(content: str) -> str:
    return str(hash(content) % ((sys.maxsize + 1) * 2))
