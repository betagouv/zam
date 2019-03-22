from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterable

import pdfkit
from pyramid.request import Request
from pyramid_jinja2 import get_jinja2_environment
from xvfbwrapper import Xvfb

from zam_repondeur.models import Amendement, Lecture


# Command-line options for wkhtmltopdf
# See https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
PDFKIT_OPTIONS = {
    "quiet": "",
    "disable-smart-shrinking": "",  # font size consistency between one amdt / all amdts
}


STATIC_PATH = Path(__file__).parent.parent / "static"
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
    env = get_jinja2_environment(request, name=".html")
    template = env.get_template(template_name)
    content: str = template.render(**context)
    return content


def write_pdf(lecture: Lecture, filename: str, request: Request) -> None:
    content = generate_html_for_pdf(request, "print.html", {"lecture": lecture})
    with xvfb_if_supported():
        pdfkit.from_string(content, filename, options=PDFKIT_OPTIONS, css=PDF_CSS)


def write_pdf_multiple(
    lecture: Lecture, amendements: Iterable[Amendement], filename: str, request: Request
) -> None:
    content = generate_html_for_pdf(
        request, "print_multiple.html", {"amendements": amendements}
    )
    with xvfb_if_supported():
        pdfkit.from_string(content, filename, options=PDFKIT_OPTIONS, css=PDF_CSS)
