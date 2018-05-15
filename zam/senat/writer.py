import csv
from typing import Iterable

from models import Amendement


FIELDS = [
    attr.name
    for attr in Amendement.__attrs_attrs__  # type: ignore
]


def filter_dict(d, key_mapping):
    return {
        key_mapping[key]: value
        for key, value in d.items()
        if key in key_mapping
    }


def write_csv(amendements: Iterable[Amendement], filename: str) -> int:
    nb_rows = 0
    with open(filename, 'w', encoding='utf-8') as file_:
        writer = csv.DictWriter(
            file_,
            fieldnames=FIELDS,
            delimiter=';',
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        for amendement in amendements:
            writer.writerow(amendement.as_dict())
            nb_rows += 1
    return nb_rows
