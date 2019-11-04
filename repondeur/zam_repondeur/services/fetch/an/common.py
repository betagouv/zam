import logging
from http import HTTPStatus
from io import BytesIO, TextIOWrapper
from typing import IO, Generator, Tuple
from zipfile import ZipFile

from zam_repondeur.services.fetch.http import get_http_session

logger = logging.getLogger(__name__)


def roman(n: int) -> str:
    if n == 15:
        return "XV"
    if n == 14:
        return "XIV"
    raise NotImplementedError


def extract_from_remote_zip(url: str) -> Generator[Tuple[str, IO[str]], None, None]:
    http_session = get_http_session()
    response = http_session.get(url)

    if response.status_code not in (HTTPStatus.OK, HTTPStatus.NOT_MODIFIED):
        message = f"Unexpected status code {response.status_code} while fetching {url}"
        logger.error(message)
        raise RuntimeError(message)

    content_type = response.headers["content-type"]
    if content_type != "application/zip":
        message = (
            f"Unexpected content type {content_type} while fetching {url} "
            "(expected application/zip)"
        )
        logger.error(message)
        raise RuntimeError(message)

    yield from extract_from_zip(BytesIO(response.content))


def extract_from_zip(content: BytesIO) -> Generator[Tuple[str, IO[str]], None, None]:
    with ZipFile(content) as zip_file:
        for filename in zip_file.namelist():
            with zip_file.open(filename) as file_:
                yield (filename, TextIOWrapper(file_, encoding="utf-8"))
