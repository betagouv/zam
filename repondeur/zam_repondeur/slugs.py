from slugify import slugify as _slugify

STOPWORDS = [
    "a",
    "au",
    "aux",
    "d",
    "dans",
    "de",
    "des",
    "du",
    "en",
    "et",
    "l",
    "la",
    "le",
    "les",
    "par",
    "pour",
    "sur",
    "un",
    "une",
]


def slugify(text: str) -> str:
    return _slugify(text, stopwords=STOPWORDS)
