import csv
from collections import Counter

from pyramid.request import Request

from zam_repondeur.models import Lecture

from .spreadsheet import FIELDS, HEADERS, export_amendement_for_spreadsheet


def write_csv(lecture: Lecture, filename: str, request: Request) -> Counter:
    counter = Counter({"amendements": 0})
    with open(filename, "w", encoding="utf-8-sig") as file_:
        file_.write(";".join(HEADERS) + "\n")
        writer = csv.DictWriter(
            file_,
            fieldnames=list(FIELDS.keys()),
            delimiter=";",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        for amendement in sorted(lecture.amendements):
            writer.writerow(export_amendement_for_spreadsheet(amendement))
            counter["amendements"] += 1
    return counter
