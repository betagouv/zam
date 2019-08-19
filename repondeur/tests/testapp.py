from pyramid.decorator import reify
from selectolax.parser import HTMLParser
from webtest import TestApp as BaseTestApp
from webtest import TestRequest as BaseTestRequest
from webtest import TestResponse as BaseTestResponse


class TestAmendement:
    def __init__(self, amendement, anchor):
        self.amendement = amendement
        self.node = anchor.parent

    def number_is_in_title(self):
        return (
            str(self.amendement.num) in self.node.css_first("header h2").text().strip()
        )

    def has_gouvernemental_class(self):
        return "gouvernemental" in self.node.attributes.get("class")


class TestResponse(BaseTestResponse):
    @reify
    def parser(self):
        return HTMLParser(self.text)

    def first_element(self, name) -> str:
        return self.parser.css_first(name).text()

    def find_amendement(self, amendement):
        anchor = self.parser.css_first(f"#amdt-{amendement.num}")
        if anchor is None:
            return None
        return TestAmendement(amendement, anchor)


class TestRequest(BaseTestRequest):
    ResponseClass = TestResponse


class TestApp(BaseTestApp):
    RequestClass = TestRequest
