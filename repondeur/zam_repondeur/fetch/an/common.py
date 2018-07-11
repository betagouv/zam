from contextlib import contextmanager
from io import BytesIO, TextIOWrapper
from typing import Generator, IO
from zipfile import ZipFile

from zam_repondeur.fetch.http import cached_session


def roman(n: int) -> str:
    if n == 15:
        return "XV"
    if n == 14:
        return "XIV"
    raise NotImplementedError


@contextmanager
def extract_from_remote_zip(url: str, filename: str) -> Generator[IO[str], None, None]:
    response = cached_session.get(url)
    assert response.headers["content-type"] == "application/zip"
    with ZipFile(BytesIO(response.content)) as zip_file:
        with zip_file.open(filename) as file_:
            yield TextIOWrapper(file_, encoding="utf-8")
