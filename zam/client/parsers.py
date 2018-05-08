from typing import IO, Union
from xml.etree import ElementTree
import zipfile

nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def qualified_name(tag: str) -> str:
    """
    A utility function to turn a namespace prefixed tag name into
    a Clark-notation qualified tag name for lxml.

    For example, ``qualified_name('p:cSld')`` returns
    ``'{http://schemas.../main}cSld'``.

    Inspiration: https://github.com/python-openxml/python-docx/
    """
    prefix, tagroot = tag.split(':')
    return f'{{{nsmap[prefix]}}}{tagroot}'


def xml2text(xml: bytes) -> str:
    """
    A string representing the textual content of this run, with content
    child elements translated to their Python equivalents.

    Inspiration: https://github.com/python-openxml/python-docx/
    """
    text = ''
    root = ElementTree.fromstring(xml)
    for child in root.iter():
        if child.tag == qualified_name('w:t'):
            t_text = child.text
            text += t_text if t_text is not None else ''
        elif child.tag == qualified_name('w:tab'):
            text += ''  # Not '\t' to avoid <pre> once commonmarked.
        elif child.tag in (qualified_name('w:br'), qualified_name('w:cr')):
            text += '\n'
        elif child.tag == qualified_name("w:p"):
            text += '\n\n'
    return text


def parse_docx(source: Union[str, IO[bytes]]) -> str:
    zipf = zipfile.ZipFile(source)
    return xml2text(zipf.read('word/document.xml'))
