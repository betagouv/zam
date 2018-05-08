from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))


def render(**data):
    return env.get_template('templates/index.html').render(**data)
