from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))


def render(**data):
    return env.get_template('zam/client/templates/index.html').render(**data)
