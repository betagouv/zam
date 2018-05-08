from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))


def render(**kwargs: dict) -> str:
    return env.get_template('templates/index.html').render(**kwargs)
