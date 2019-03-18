from collections import namedtuple
from difflib import Differ
from html import escape
from itertools import groupby
from operator import attrgetter
from typing import List


differ = Differ()
Diff = namedtuple("Diff", ["code", "word"])

CODES_TO_TAGS = {"+ ": "ins", "- ": "del", "  ": None}


def html_diff(old_text: str, new_text: str) -> str:
    old_words = old_text.split()
    new_words = new_text.split()
    deltas = (
        Diff(delta[:2], delta[2:]) for delta in differ.compare(old_words, new_words)
    )
    html_fragments = (
        wrap_with_tag(code, [diff.word for diff in diffs])
        for code, diffs in groupby(deltas, key=attrgetter("code"))
        if code != "? "
    )
    return " ".join(html_fragments).strip()


def wrap_with_tag(code: str, words: List[str]) -> str:
    tag = CODES_TO_TAGS[code]
    text = escape(" ".join(words))
    if tag:
        return f"<{tag}>{text}</{tag}>"
    return text
