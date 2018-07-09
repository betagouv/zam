from pyramid.decorator import reify
from selectolax.parser import HTMLParser
from webtest import (
    TestApp as BaseTestApp,
    TestRequest as BaseTestRequest,
    TestResponse as BaseTestResponse,
)


class TestResponse(BaseTestResponse):
    @reify
    def parser(self):
        return HTMLParser(self.text)


class TestRequest(BaseTestRequest):
    ResponseClass = TestResponse


class TestApp(BaseTestApp):
    RequestClass = TestRequest
