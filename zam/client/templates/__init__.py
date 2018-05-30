from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from logbook import Logger

from models import Articles, Amendements, Reponses
from utils import build_output_filename

log = Logger("client")
env = Environment(
    loader=FileSystemLoader("."),
    # Strip down as much as possible the size of the HTML
    # by avoiding extra white spaces everywhere.
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(**kwargs: dict) -> str:
    return env.get_template("templates/index.html").render(**kwargs)


def write_html(html: str, output_filename: Path) -> None:
    with open(output_filename, "w") as output_file:
        output_file.write(html)
        log.info(f"HTML generated on {output_filename}")


def render_and_save_html(
    title: str,
    articles: Articles,
    amendements: Amendements,
    reponses: Reponses,
) -> str:
    html = render(
        **{"title": title, "articles": articles, "reponses": reponses}
    )
    write_html(html, build_output_filename())
    return html
