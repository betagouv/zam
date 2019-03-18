from difflib import Differ
from itertools import groupby
from operator import itemgetter
from typing import List


differ = Differ()


TAGS = {"+": "ins", "-": "del", " ": None}


def text_to_html(old: str, new: str) -> str:
    old_words = old.split()
    new_words = new.split()
    deltas = ((delta[0], delta[2:]) for delta in differ.compare(old_words, new_words))
    grouped_deltas = (
        (key, [item[1] for item in items])
        for key, items in groupby(deltas, key=itemgetter(0))
        if key != "?"
    )
    html = " ".join(wrap_with_tag(key, words) for key, words in grouped_deltas if words)
    return html.strip()


def wrap_with_tag(key: str, words: List[str]) -> str:
    tag = TAGS[key]
    text = " ".join(words)
    if tag:
        return f"<{tag}>{text}</{tag}>"
    return text
