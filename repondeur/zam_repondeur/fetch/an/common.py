import logging
from contextlib import contextmanager
from io import BytesIO, TextIOWrapper
from typing import Generator, IO
from zipfile import ZipFile

from zam_repondeur.fetch.http import cached_session


logger = logging.getLogger(__name__)


def roman(n: int) -> str:
    if n == 15:
        return "XV"
    if n == 14:
        return "XIV"
    raise NotImplementedError


@contextmanager
def extract_from_remote_zip(url: str, filename: str) -> Generator[IO[str], None, None]:
    response = cached_session.get(url)

    if response.status_code != 200:
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

    with ZipFile(BytesIO(response.content)) as zip_file:
        with zip_file.open(filename) as file_:
            yield TextIOWrapper(file_, encoding="utf-8")
