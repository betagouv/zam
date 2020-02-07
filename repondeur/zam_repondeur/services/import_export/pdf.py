from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

import pdfkit
from pyramid.request import Request
from xvfbwrapper import Xvfb

from zam_repondeur.models import Amendement, AmendementList, Lecture
from zam_repondeur.templating import render_template

# Command-line options for wkhtmltopdf
# See https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
PDFKIT_OPTIONS = {
    "quiet": "",
    "disable-smart-shrinking": "",  # font size consistency between one amdt / all amdts
    "outline-depth": 3,
}


STATIC_PATH = Path(__file__).parent.parent.parent / "static"
PDF_CSS = str(STATIC_PATH / "css" / "print.css")


@contextmanager
def xvfb_if_supported() -> Generator:
    try:
        with Xvfb():
            yield
    except (EnvironmentError, OSError, RuntimeError):
        yield


def generate_html_for_pdf(request: Request, template_name: str, context: dict) -> str:
    """Mostly useful for testing purpose."""
    return render_template(template_name, context, registry=request.registry)


def write_pdf(lecture: Lecture, filename: str, request: Request) -> None:
    content = generate_html_for_pdf(request, "print/all.html", {"lecture": lecture})
    with xvfb_if_supported():
        pdfkit.from_string(content, filename, options=PDFKIT_OPTIONS, css=PDF_CSS)


def write_pdf_multiple(
    lecture: Lecture,
    amendements: Iterable[Amendement],
    filename: str,
    request: Request,
) -> None:
    all_amendements: AmendementList = lecture.all_amendements
    content = generate_html_for_pdf(
        request,
        "print/multiple.html",
        {"amendements": amendements, "all_amendements": all_amendements},
    )
    with xvfb_if_supported():
        pdfkit.from_string(content, filename, options=PDFKIT_OPTIONS, css=PDF_CSS)
