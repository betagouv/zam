from datetime import datetime
from pathlib import Path
import os
from typing import Iterator

from logbook import warn

from decorators import require_env_vars
from templates import render, write_html


def strip_styles(content: str) -> str:
    return content.replace(' style="text-align:justify;"', '')


def warnumerate(items: list, limit: int) -> Iterator[dict]:
    for index, raw_article in enumerate(items):
        if limit and index >= limit:
            warn(f'Only {limit} items loaded.')
            break
        yield raw_article


@require_env_vars(env_vars=['ZAM_OUTPUT'])
def build_output_filename(output_path: str) -> Path:
    output_root_path = Path(output_path)
    current_branch = os.popen('git symbolic-ref --short HEAD').read().strip()
    if current_branch == 'master':
        return output_root_path / 'index.html'
    now = datetime.utcnow()
    output_dir = f'{now.isoformat()[:len("YYYY-MM-DD")]}-{current_branch}'
    output_path = output_root_path / output_dir
    output_path.mkdir(exist_ok=True)
    return output_path / 'index.html'


def render_and_save_html(title, articles, amendements, reponses):
    html = render(title=title, articles=articles, reponses=reponses)
    output_filename = build_output_filename()
    write_html(html, output_filename)
