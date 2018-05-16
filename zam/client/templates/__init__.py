from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from logbook import Logger

log = Logger('client')
env = Environment(loader=FileSystemLoader('.'),
                  # Strip down as much as possible the size of the HTML
                  # by avoiding extra white spaces everywhere.
                  trim_blocks=True, lstrip_blocks=True)


def render(**kwargs: dict) -> str:
    return env.get_template('templates/index.html').render(**kwargs)


def write_html(html: str, output_filename: Path) -> None:
    with open(output_filename, 'w') as output_file:
        output_file.write(html)
        log.info(f'HTML generated on {output_filename}')
