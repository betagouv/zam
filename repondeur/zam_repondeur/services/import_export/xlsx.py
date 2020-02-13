from collections import Counter
from typing import Iterable, List, Optional

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pyramid.request import Request

from zam_repondeur.models import Amendement, Lecture

from .spreadsheet import FIELDS, HEADERS, export_amendement_for_spreadsheet


def write_xlsx(
    lecture: Lecture,
    filename: str,
    request: Request,
    amendements: Optional[List[Amendement]] = None,
) -> Counter:
    wb = Workbook()
    ws = wb.active
    ws.title = "Amendements"
    amendements = amendements or sorted(lecture.amendements)

    _write_xslsx_header_row(ws)
    counter = _export_xlsx_data_rows(ws, amendements)
    wb.save(filename)
    return counter


def _write_xslsx_header_row(ws: Worksheet) -> None:
    for column, value in enumerate(HEADERS, 1):
        cell = ws.cell(row=1, column=column)
        cell.value = value


def _export_xlsx_data_rows(ws: Worksheet, amendements: Iterable[Amendement]) -> Counter:
    counter = Counter({"amendements": 0})
    for amend in amendements:
        amend_dict = {
            FIELDS[k]: v for k, v in export_amendement_for_spreadsheet(amend).items()
        }
        for column, value in enumerate(HEADERS, 1):
            cell = ws.cell(row=counter["amendements"] + 2, column=column)
            cell.value = amend_dict[value]
        counter["amendements"] += 1
    return counter
