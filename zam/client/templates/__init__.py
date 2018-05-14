from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'),
                  # Strip down as much as possible the size of the HTML
                  # by avoiding extra white spaces everywhere.
                  trim_blocks=True, lstrip_blocks=True)


def render(**kwargs: dict) -> str:
    return env.get_template('templates/index.html').render(**kwargs)
