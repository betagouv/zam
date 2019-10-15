import os
from contextlib import contextmanager
from datetime import datetime
from string import Template

from pytz import UTC


class NginxFriendlyTemplate(Template):
    delimiter = "$$"


@contextmanager
def template_local_file(template_filename, output_filename, data):
    with open(template_filename, encoding="utf-8") as template_file:
        template = NginxFriendlyTemplate(template_file.read())
    with open(output_filename, mode="w", encoding="utf-8") as output_file:
        output_file.write(template.substitute(**data))
    yield
    os.remove(output_filename)


def timestamp():
    return UTC.localize(datetime.utcnow()).isoformat(timespec="seconds")
