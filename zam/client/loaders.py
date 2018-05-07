import json
from io import BytesIO

import pdfminer.high_level

from decorators import check_existence
from parsers import parse_docx


def load_json(source_path):
    with open(source_path) as source:
        return json.loads(source.read())


@check_existence
def load_pdf(source_path, codec='latin-1'):
    target = BytesIO()
    with open(source_path, 'rb') as source:
        pdfminer.high_level.extract_text_to_fp(source, target, codec=codec)
    content = target.getvalue().decode()
    # Skip optional headers.
    separator = '----------'
    if separator in content:
        headers, content = content.split(separator)
    return content.strip()


@check_existence
def load_docx(source_path):
    with open(source_path, 'rb') as source:
        content = parse_docx(source)
    # Get rid of (not proper docx) headers.
    return '\n'.join(part for part in content.split('\n')[9:])
