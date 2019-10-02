from requests import Response


class NotFound(Exception):
    pass


class FetchError(Exception):
    def __init__(self, url: str, response: Response) -> None:
        self.url = url
        self.response = response
