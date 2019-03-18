from difflib import Differ
from html import escape
from itertools import groupby
from operator import itemgetter
from typing import List


differ = Differ()


TAGS = {"+": "ins", "-": "del", " ": None}


def html_diff(old: str, new: str) -> str:
    old_words = old.split()
    new_words = new.split()
    deltas = ((delta[0], delta[2:]) for delta in differ.compare(old_words, new_words))
    html_fragments = (
        wrap_with_tag(key, list(zip(*items))[1])
        for key, items in groupby(deltas, key=itemgetter(0))
        if key != "?"
    )
    return " ".join(html_fragments).strip()


def wrap_with_tag(key: str, words: List[str]) -> str:
    tag = TAGS[key]
    text = escape(" ".join(words))
    if tag:
        return f"<{tag}>{text}</{tag}>"
    return text
