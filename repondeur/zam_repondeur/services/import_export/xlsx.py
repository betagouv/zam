from collections import Counter
from typing import Iterable, List, Optional

from openpyxl import Workbook
from openpyxl.styles import Color, Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from pyramid.request import Request

from zam_repondeur.models import Amendement, Lecture

from .spreadsheet import FIELDS, HEADERS, export_amendement_for_spreadsheet

DARK_BLUE = Color(rgb="00182848")
WHITE = Color(rgb="00FFFFFF")


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
        cell.fill = PatternFill(patternType="solid", fgColor=DARK_BLUE)
        cell.font = Font(color=WHITE, sz=8)


def _export_xlsx_data_rows(ws: Worksheet, amendements: Iterable[Amendement]) -> Counter:
    counter = Counter({"amendements": 0})
    for amend in amendements:
        amend_dict = {
            FIELDS[k]: v for k, v in export_amendement_for_spreadsheet(amend).items()
        }
        for column, value in enumerate(HEADERS, 1):
            cell = ws.cell(row=counter["amendements"] + 2, column=column)
            cell.value = amend_dict[value]
            cell.font = Font(sz=8)
        counter["amendements"] += 1
    return counter
